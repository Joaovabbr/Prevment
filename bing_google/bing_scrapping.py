import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import urllib.parse
from sqlite_handler import SQLiteHandler

options = Options()
options.add_argument("--headless=new")
options.headless = False  # roda o Chrome sem abrir janela

driver = webdriver.Chrome(options=options)

busca = 'Openai'
tema = ''
busca_url = urllib.parse.quote(busca + ' ' + tema)
url = f'https://www.bing.com/news/search?q={busca_url}&go=Pesquisar&qs=ds&form=QBNT'

db_path = Path(__file__).parent / "dados_bing_google.db"
sqlite = SQLiteHandler(db_path)
sqlite.setup_table("noticias", {
    "id": "TEXT PRIMARY KEY",
    "entity": "TEXT",
    "title": "TEXT",
    "url": "TEXT",
    "owner": "TEXT",
    "date": "TEXT"
})
QTD_NOTICIAS = 500
news_titles  = []

driver.get(url)

time.sleep(5)  # espera carregar o JS, ajustar conforme necessidade
j = 0
last_height = None
tentativas = 0
while j < QTD_NOTICIAS:
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        tentativas += 1
        if tentativas > 3: break
    last_height = new_height
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    noticias = soup.find_all('div', class_='news-card-body')

    for noticia in noticias:
        fonte_div = noticia.find('div', class_='source set_top')
        if fonte_div:
            fonte_a = fonte_div.find('a')
            fonte = fonte_a.text.strip() if fonte_a else 'Sem fonte'
            tempo_span = fonte_div.find('span', tabindex="0")
            tempo = tempo_span.text.strip() if tempo_span else 'Sem tempo'
        else:
            fonte = 'Sem fonte'
            tempo = 'Sem tempo'

        titulo_a = noticia.find('a', class_='title')
        titulo = titulo_a.text.strip() if titulo_a else 'Sem título'
        url_noticia = titulo_a['href'] if titulo_a else 'Sem URL'
        if not titulo in news_titles:
            print("Adicionando notícia ",j )
            news_titles.append(titulo)
            sqlite.insert_data("noticias", {
                "id": sqlite.news_id(titulo, url_noticia, fonte, tempo),
                "entity": busca,
                "title": titulo,
                "url": url_noticia,
                "owner": fonte,
                "date": tempo
            })
            j += 1
        scroll_distance = 170
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")

driver.quit()
