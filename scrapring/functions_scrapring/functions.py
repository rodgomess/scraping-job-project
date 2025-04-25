from playwright.async_api import async_playwright
import asyncio
import pandas as pd
from datetime import datetime
import os

def chunk_list(lst, size):
    """
    Divide uma lista em partes menores (chunks) de tamanho fixo.

    Parâmetros:
        lst (list): Lista a ser dividida.
        size (int): Tamanho de cada pedaço (chunk).

    Retorna:
        generator: Um gerador que produz sublistas da lista original com no máximo 'size' elementos.
    """

    for i in range(0, len(lst), size):
        yield lst[i:i + size]


async def extract_basic_info_job(page):
    """Extrai salário, local e regime de trabalho da vaga."""
    info = {}
    try:
        itens = page.locator("div.infoVaga ul li")
        info['salario'] = await itens.nth(0).locator('div').inner_text()
        info['local'] = await itens.nth(1).locator('div span.info-localizacao').inner_text()
        info['regime_trabalista'] = await itens.nth(2).locator('div').inner_text()
    except Exception as e:
        print(f"[!] Erro ao extrair info básica: {e}")
        info['salario'] = None
        info['local'] = None
        info['regime_trabalista'] = None
    return info

async def extract_benefits_job(page):
    """Extrai os benefícios listados na vaga."""
    beneficios = []
    try:
        lista = page.locator("div.job-tab-content.job-benefits ul li")
        total = await lista.count()
        for i in range(total):
            texto = await lista.nth(i).locator('span.benefit-label').inner_text()
            beneficios.append(texto)
    except Exception as e:
        print(f"[!] Erro ao extrair benefícios: {e}")
    return beneficios

async def get_info_job(link, context):
    """Abre a página da vaga e retorna as informações extraídas."""
    page = await context.new_page()
    completed_link = f'https://www.vagas.com.br{link}'
    
    try:
        await page.goto(completed_link, wait_until="domcontentloaded")
        info = await extract_basic_info_job(page)
        info['beneficios'] = await extract_benefits_job(page)
        info['link'] = completed_link
        info['erro'] = None

    except Exception as e:
        print(f"[!] Erro ao acessar vaga {completed_link}: {e}")
        info = {
            "salario": None,
            "local": None,
            "regime_trabalista": None,
            "beneficios": [],
            "link": completed_link,
            "erro": str(e)
        }
    await page.close()
    return info

async def get_link_jobs(page):

    # Site contendo vagas de tecnologia em forma de lista resumida
    await page.goto("https://www.vagas.com.br/vagas-de-tecnologia", wait_until="domcontentloaded")
    await page.wait_for_selector("#todasVagas ul li.vaga")

    # Lista de elemento contendo link para a vaga
    jobs = page.locator("#todasVagas ul li.vaga")
    total = await jobs.count()
    print(f"Total de vagas encontradas: {total}")

    # Criando uma lista de links
    links_job = [
        await jobs.nth(i).locator('a.link-detalhes-vaga').get_attribute("href")
        for i in range(total)
    ]

    # Remove possíveis None
    links_job = [link for link in links_job if link]  
    return links_job


async def parallelize_extract(links_job, chunk_size, context):
    output = []
    for grupo in chunk_list(links_job, chunk_size):
        print(f"🔄 Processando grupo com {len(grupo)} links...")
        output_set = await asyncio.gather(*(get_info_job(link, context) for link in grupo))
        output.extend(output_set)
    
    return output

def save_output(output):
    # Path para salvar
    current_date = datetime.now().date()

    # Definindo o caminho do diretório e do arquivo
    directory_path = f"datalake/vagasdotcom/{current_date}"
    file_path = f"{directory_path}/vagas_extraidas.csv"
    
    # Criando Data Frame
    df = pd.DataFrame(output)

    # Adicionando campos de controle
    df['datetime_execution'] = pd.to_datetime(datetime.now())
    df['date_execution'] = pd.to_datetime(datetime.now().date())

    # Verificando se o diretório existe, se não, criando-o
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    # Salvando os dados
    df.to_csv(file_path, index=False)
    print(f"✅ Dados salvos com sucesso em: {file_path}")