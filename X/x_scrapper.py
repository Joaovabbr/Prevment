import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
from playwright.sync_api import sync_playwright
import time
import urllib.parse
import os
from dotenv import load_dotenv
from pathlib import Path
from sqlite_handler import SQLiteHandler
load_dotenv()


user = os.getenv("TW_USER")
email = os.getenv("TW_EMAIL")
pwd = os.getenv("TW_PASSWORD")
default_browser_path = os.getenv("BROWSER_PATH")

sqlite = SQLiteHandler("./x/x_posts.db")
sqlite.setup_table("posts", {
    "id": "TEXT PRIMARY KEY",
    "entity": "TEXT",
    "user": "TEXT",
    "text": "TEXT",
    "likes": "INTEGER",
    "shares": "INTEGER",
    "coments": "INTEGER",
    "views": "INTEGER"
})

termo = 'OpenAi'
tema = ''
termo_url = urllib.parse.quote(termo + ' ' + tema)
search_url = f"https://x.com/search?q={termo_url}&src=typed_query&f=live"
browser_data_path = Path(__file__).parent / "browser_data"
QTD_POSTS = 700
TIMEOUT = 1000
posts_text = []

def text_to_num(texto):
    """
    Converte texto com sufixo como '10K', '1.2M' para número inteiro.
    """
    texto = texto.strip().upper().replace(",", ".")
    if texto.endswith("K"):
        return int(float(texto[:-1]) * 1000)
    elif texto.endswith("M"):
        return int(float(texto[:-1]) * 1000000)
    else:
        try:
            return int(float(texto))
        except:
            return 0
        
def process_post(post):
    # Dividir em linhas e remover linhas vazias
    if not post.is_visible(timeout=2000):
        time.sleep(1)
        return None
    if not post.all_inner_texts() or len(post.all_inner_texts()) == 0:
        return None
    linhas = [linha.strip() for linha in post.all_inner_texts()[0].strip().split('\n') if linha.strip() != '']
    user = linhas[0] if linhas else 'Desconhecido'
    data = linhas[3] if len(linhas) > 3 else 'Desconhecido'
    texto = linhas[4] if len(linhas) > 4 else 'Desconhecido'
    if 'replying' in texto.lower(): texto = linhas[6]
    dados = post.locator("div[role='group']")
    aria_label = dados.get_attribute("aria-label")
    if aria_label: aria_label = aria_label.strip().split(',')
    likes = 0
    shares = 0
    coments = 0
    views = 0
    for info in aria_label:
        if 'likes' in info.lower():
            likes = text_to_num(info[:info.index('likes')].strip())
        if 'views' in info.lower():
            views = text_to_num(info[:info.index('views')].strip())
        if 'replies' in info.lower():
            coments = text_to_num(info[:info.index('replies')].strip())
        if 'reposts' in info.lower():
            shares = text_to_num(info[:info.index('reposts')].strip())
    return {
        'user': user,
        'data': data,
        'texto': texto,
        'likes': likes,
        'shares': shares,
        'coments': coments,
        'views': views
    }


with sync_playwright() as p:
    navegador = p.chromium.launch_persistent_context(user_data_dir=browser_data_path,  # pode ser outro diretório
            headless=True,
            executable_path=default_browser_path,)
    page = navegador.new_page()
    page.goto("https://x.com/login")
    time.sleep(1)
    for p in navegador.pages:
            if not p.url == 'https://v6.gxcorner.games/' and not 'home' in p.url.lower() : p.close()
    if page.locator("input[name='text']").is_visible():
        page.fill("input[name='text']", email)
        page.click("text='Avançar'")
    elif page.locator("input[name='password']").is_visible():
        page.fill("input[name='text']", user)
        page.click("text='Avançar'")

    page.goto(search_url)
    contador_posts=0
    while contador_posts < QTD_POSTS:
        page.wait_for_selector("article")
        posts = page.locator("article")
        qtd_posts = posts.count()
        for i in range(qtd_posts):
            try: 
                if i > posts.count():
                    break
                post = posts.nth(i)
                post_dict = process_post(post)
                if not post_dict or post_dict['texto'] in posts_text:
                    height = post.bounding_box()['height']
                    page.evaluate(f"window.scrollBy(0, {height})")
                    time.sleep(2/100)
                    continue
                posts_text.append(post_dict['texto'])
                sqlite.insert_data("posts", {
                    "id": sqlite.post_id(post_dict['texto'], post_dict['likes'], post_dict['coments'], post_dict['shares']),
                    "entity": termo,
                    "user": post_dict['user'],
                    "text": post_dict['texto'],
                    "likes": post_dict['likes'],
                    "shares": post_dict['shares'],
                    "coments": post_dict['coments'],
                    "views": post_dict['views']
                })
                contador_posts+=1
                height = post.bounding_box()['height']
                page.evaluate(f"window.scrollBy(0, {height})")
                time.sleep(2/100)
            except Exception as e:
                print(f"Erro ao processar post {contador_posts}: {e}")
                time.sleep(1)
                continue


    navegador.close()