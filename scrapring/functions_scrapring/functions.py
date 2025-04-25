from playwright.async_api import async_playwright
import asyncio
from datetime import datetime

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
    """
    Extrai informações basicas como nome, regime trabalista e etc

    Parâmetros:
        page: Pagina contida no browser

    Retorna:
        dict: Um dicionario contendo informações da vaga
    """

    info = {}
    try:
        # Cargo
        info['cargo'] = await page.locator("h1").inner_text()

        # Nome da empresa
        info['nome_empresa'] = await page.locator("h2.job-shortdescription__company").inner_text()

        # Data de plublicação
        info['nome_empresa'] = await page.locator("h2.job-shortdescription__company").inner_text()

        # Lista de intens contendo Salario, Local e Regime Trabalista
        itens = page.locator("div.infoVaga ul li")
        info['salario'] = await itens.nth(0).locator('div').inner_text()
        info['local'] = await itens.nth(1).locator('div span.info-localizacao').inner_text()
        info['regime_trabalista'] = await itens.nth(2).locator('div').inner_text()

    except Exception as e:
        print(f"[!] Erro ao extrair info básica: {e}")
        info['cargo'] = None
        info['nome_empresa'] = None
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

async def get_link_jobs(page, times_click_see_more):

    # Site contendo vagas de tecnologia em forma de lista resumida
    await page.goto("https://www.vagas.com.br/vagas-de-tecnologia", wait_until="domcontentloaded")
    # await page.wait_for_selector("#todasVagas ul li.vaga")

    for _ in range(times_click_see_more):
        try:
            await page.get_by_role("link", name="mostrar mais vagas").click()
            await page.wait_for_timeout(500)  # Dá um pequeno tempo pra página carregar
        except Exception as e:
            print(f"Não foi possível clicar em 'mostrar mais vagas': {e}")
            break

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