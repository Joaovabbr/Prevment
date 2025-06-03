import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://news.google.com/search?q=zara&hl=pt-BR&gl=BR&ceid=BR:pt-419'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = soup.find_all('article')

    dados = []

    for article in articles:
        title_tag = article.find('a', class_='JtKRv')
        title = title_tag.text.strip() if title_tag else 'Sem título'

        link_tag = article.find('a', class_='WwrzSb')
        url_noticia = 'https://news.google.com' + link_tag['href'][1:] if link_tag else 'Sem URL'

        fonte_tag = article.find('div', class_='vr1PYe')
        fonte = fonte_tag.text.strip() if fonte_tag else 'Sem fonte'

        tempo_tag = article.find('time')
        tempo = tempo_tag.text.strip() if tempo_tag else 'Sem tempo'

        dados.append({
            'titulo': title,
            'url': url_noticia,
            'fonte': fonte,
            'tempo': tempo
        })

    df = pd.DataFrame(dados)

    print(df)
else:
    print('Erro na requisição:', response.status_code)
