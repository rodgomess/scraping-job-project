from playwright.async_api import async_playwright
import asyncio
from datetime import datetime
import argparse
import random
import pandas as pd
import re
import os

def parse_args():
    parser = argparse.ArgumentParser()
    # Defina tudo num dicionário; o laço cuida do resto
    arg_defs = {
        "search_word":        dict(type=str,   default="Dentista",     help="Palavra chave de busca"),
        "order_by":           dict(type=str,   default="mais_recente", help="Ordenação das vagas"),
        "filter_list":        dict(action="append", default=[],        help="Filtros usados para extração"),
        "times_click_see_more": dict(type=int, default=0,             help="Cliques em 'ver mais'")
    }
    for name, opts in arg_defs.items():
        parser.add_argument(f"--{name}", **opts)
    return parser.parse_args()

def save_output(output, search_word):
    # Path para salvar
    current_date = datetime.now().date()

    # Definindo o caminho do diretório e do arquivo
    directory_path = f"data_base/datalake/vagasdotcom"
    file_path = f"{directory_path}/extract.csv"
    
    # Criando Data Frame
    df = pd.DataFrame(output)

    # Adicionando campos de controle
    df['palavra_busca'] = pd.Series(search_word, index=df.index)
    df['datetime_execution'] = pd.to_datetime(datetime.now())
    df['date_execution'] = pd.to_datetime(datetime.now().date())

    # Verificando se o diretório existe, se não, criando-o
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    # Salvando os dados
    df.to_csv(file_path, index=False)
    print(f"Dados salvos com sucesso em: {file_path}")

async def click_filter(page, nome_filtro):
    """
    Clica no link do filtro baseado no texto sem contar o número de vagas.

    Args:
        page: página Playwright
        nome_filtro: nome limpo que o usuário forneceu ("Na empresa", "Regime CLT", etc.)
        container_id: id do container onde buscar (ex: "#pesquisaFiltros")
    """
    container = page.locator('#pesquisaFiltros')
    links = container.locator("a")
    total_links = await links.count()

    for i in range(total_links):
        link = links.nth(i)
        texto = await link.inner_text()

        # Limpar o texto: remover tudo que estiver entre parênteses
        texto_limpo = re.sub(r'\s*\(.*?\)', '', texto).strip()

        if texto_limpo == nome_filtro:
            await link.click()
            print(f"Clicado no filtro: {nome_filtro}")
            return

    print(f"Filtro '{nome_filtro}' não encontrado!")

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
    Extrai informações básicas da vaga: cargo, empresa, local, salário, regime.

    Args:
        page: Página do Playwright.

    Returns:
        dict: Informações básicas da vaga.
    """

    info = {}
    try:
        # Cargo
        info['cargo'] = await page.locator("h1").inner_text()

        # Nome da empresa
        info['nome_empresa'] = await page.locator("h2.job-shortdescription__company").inner_text()

        # Data de plublicação
        info['data_publicacao'] = await page.locator("div.job-info__container ul.job-breadcrumb li").nth(0).inner_text()

        # Lista de intens contendo Salario, Local e Regime Trabalista
        itens = page.locator("div.infoVaga ul li")
        info['salario'] = await itens.nth(0).locator('div').inner_text()
        info['local'] = await itens.nth(1).locator('div span.info-localizacao').inner_text()
        info['regime_trabalista'] = await itens.nth(2).locator('div').inner_text()

    except Exception as e:
        print(f"[!] Erro extraindo informações básicas: {e}")
        info = {k: None for k in ['cargo', 'nome_empresa', 'salario', 'local', 'regime_trabalhista']}

    return info

async def extract_benefits_job(page):
    """
    Extrai os benefícios listados na vaga.

    Args:
        page: Página do Playwright.

    Returns:
        list: Lista de benefícios.
    """

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

async def extract_job_info(link, context):
    """
    Abre a página da vaga e extrai todas as informações disponíveis.

    Args:
        link (str): Caminho relativo da vaga.
        context: Contexto do navegador Playwright.

    Returns:
        dict: Informações completas da vaga.
    """

    page = await context.new_page()
    completed_link = f'https://www.vagas.com.br{link}'
    job_info = {}
    
    try:
        await page.goto(completed_link, wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(1, 2)) # Delay para evitar bloqueios

        job_info = await extract_basic_info_job(page)
        job_info['beneficios'] = await extract_benefits_job(page)
        job_info['link'] = completed_link
        job_info['erro'] = None

    except Exception as e:
        print(f"[!] Erro ao acessar vaga {completed_link}: {e}")
        job_info = {
            'cargo': None,
            'nome_empresa': None,
            "salario": None,
            "local": None,
            "regime_trabalista": None,
            "beneficios": [],
            "link": completed_link,
            "erro": str(e)
        }
    await page.close()

    return job_info

async def collect_job_links(page, times_click_see_more, search_word, filter_list, order_by="mais_recentes"):
    """
    Coleta todos os links de vagas da página inicial.

    Args:
        page: Página inicial do Playwright.
        times_click_see_more (int): Número de vezes que deve clicar em "mostrar mais vagas".

    Returns:
        list: Lista de links de vagas.
    """

    # Site contendo vagas de tecnologia em forma de lista resumida
    link_base = "https://www.vagas.com.br"
    search_word = f"/vagas-de-{search_word}"
    order_by = f"?ordenar_por={order_by}"

    await page.goto(f"{link_base}{search_word}{order_by}", wait_until="domcontentloaded")
    
    # Clicar em todos os ver mais filtros para que qualquer filtro selecionado fique clicavel
    more_filters = "+ (mais)"
    total_more_filters = await page.locator(f'text={more_filters}').count()
    for i in range(total_more_filters):
        try:
            await page.get_by_text(more_filters).nth(0).click()
        except Exception as e:
            print(f"Não foi possível clicar em 'mais filtros': {e}")

    # Clicar exatamente nos filtros selecionados
    for filter in filter_list:
        try:
            # await page.locator("#pesquisaFiltros").get_by_role("link", name=filter, exact=False).click()
            await click_filter(page, filter)
        except Exception as e:
            print(f"Não foi possível clicar no filtro {filter}': {e}")

    # Clicar em ver mais para aparecer mais vagas
    for _ in range(times_click_see_more):
        try:
            await page.get_by_role("link", name="mostrar mais vagas").click()
            await page.wait_for_timeout(300)  # Dá um pequeno tempo pra página carregar
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
    return [link for link in links_job if link]


async def parallelize_extract(links_job, context, chunk_size=5):
    """
    Processa a extração de todas as vagas em paralelo, controlando a quantidade simultânea.

    Args:
        links (list): Lista de links de vagas.
        context: Contexto do navegador Playwright.
        chunk_size (int): Número máximo de vagas processadas em paralelo.

    Returns:
        list: Lista de informações extraídas das vagas.
    """
    output = []
    for grupo in chunk_list(links_job, chunk_size):
        print(f"Processando grupo com {len(grupo)} vagas simultaneamente...")
        output_set = await asyncio.gather(*(extract_job_info(link, context) for link in grupo))
        output.extend(output_set)
    
    return output