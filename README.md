# 🔍 Vagas Scraper com Streamlit

Um projeto de Web Scraping com interface interativa desenvolvido com **Playwright**, **Pandas** e **Streamlit**, voltado para extração e visualização de vagas de emprego do site [vagas.com](https://www.vagas.com.br).

---

## 🧠 Visão Geral

Este projeto permite extrair vagas a partir de palavras-chave e filtros específicos diretamente pela interface do Streamlit. Ideal para profissionais ou estudantes que desejam automatizar a coleta de oportunidades do site Vagas.com.

---

## ⚙️ Tecnologias Utilizadas

- [Playwright](https://playwright.dev/python/): para automação de navegação e scraping
- [Streamlit](https://streamlit.io/): interface gráfica web para facilitar a interação
- [Pandas](https://pandas.pydata.org/): tratamento e análise de dados
- `subprocess`: para rodar processos externos (scraper) dentro do Streamlit

---

## 🧩 Como Funciona

1. **Interface em Streamlit** permite:
   - Digitar palavras-chave
   - Aplicar filtros personalizados
   - Iniciar a extração com um clique no botão

2. **Execução do Scraper**:
   - Um `subprocess` chama o script com Playwright
   - Diversas abas são abertas simultaneamente para maior velocidade
   - As vagas são salvas em um CSV na pasta `datalake/`

3. **Processamento de Dados**:
   - Um notebook carrega os dados do CSV recém-gerado
   - Se for a primeira execução: os dados são salvos em um `path histórico`
   - Se já existir histórico: faz `union`, remove duplicatas com `drop_duplicates()` e salva novamente

4. **Visualização e Filtros**:
   - Os dados limpos são exibidos no Streamlit
   - Filtros podem ser aplicados em qualquer coluna diretamente na interface

---

## 💡 Diferenciais
Automação 100% funcional com múltiplas abas (paralelismo leve)

Integração entre scraping e frontend interativo

Histórico de dados para análise contínua

Nenhuma duplicidade de vagas no histórico

Filtros dinâmicos em todas as colunas

---

## 📌 Observações
Este projeto é apenas para fins educacionais e de portfólio. Respeite os termos de uso do vagas.com.

Caso deseje adaptar para outros sites, a estrutura está modularizada.

---

## 📷 Screenshots

---

## 🧑‍💻 Autor
Rodrigo Gomes
🔗 [LinkedIn](https://www.linkedin.com/in/rodrigogomes-profile/)