import sys
import os

# Garatindo que abspath é o caminho raiz do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions_scrapring.functions import get_link_jobs, parallelize_extract
from utils.helper import save_output
from playwright.async_api import async_playwright
import asyncio

async def main():
    async with async_playwright() as p:
        # Configurando o browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Criando uma lista de links
            links_job = await get_link_jobs(page)
            
            # Quantidade total de chunks
            chunk_size = 50

            # Processamento paralelizado em chunks
            output = await parallelize_extract(links_job, chunk_size, context)

        finally:
            # Fechando o browser
            await browser.close()

    # Trasforma os dados em um dataframe e salva como csv
    save_output(output)

if __name__ == "__main__":
    asyncio.run(main())