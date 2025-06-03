import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.bing.com/news/search?q=zara&go=Pesquisar&qs=ds&form=QBNT'  

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
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
else:
    print('Erro na requisição:', response.status_code)
