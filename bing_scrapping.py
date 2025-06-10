from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

options = Options()
options.headless = True  # roda o Chrome sem abrir janela

driver = webdriver.Chrome(options=options)

url = 'https://www.bing.com/news/search?q=zara&go=Pesquisar&qs=ds&form=QBNT'

driver.get(url)

time.sleep(5)  # espera carregar o JS, ajustar conforme necessidade

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

noticias = soup.find_all('div', class_='t_t')

dados = []
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

    dados.append({
        'titulo': titulo,
        'url': url_noticia,
        'fonte': fonte,
        'tempo': tempo
    })

df = pd.DataFrame(dados)
print(df)

with open("dados/dados_bing.json", "w", encoding="utf-8") as arquivo:
    json.dump(dados, arquivo, ensure_ascii=False, indent=4)

driver.quit()
