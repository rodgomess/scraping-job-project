from playwright.async_api import async_playwright
import asyncio
import sys
import os

# Garatindo que abspath é o caminho raiz do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions_extract import collect_job_links, parallelize_extract, save_output, parse_args

async def main():
    args = parse_args()

    async with async_playwright() as p:
        # Configurando o browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Criando uma lista de links
            links_job = await collect_job_links(page, args.times_click_see_more, args.search_word, args.filter_list, args.order_by)
            
            # Quantidade total de chunks
            chunk_size = 40

            # Processamento paralelizado em chunks
            output = await parallelize_extract(links_job, context, chunk_size)

        finally:
            # Fechando o browser
            await browser.close()

    # Trasforma os dados em um dataframe e salva como csv
    save_output(output, args.search_word)

if __name__ == "__main__":
    asyncio.run(main())