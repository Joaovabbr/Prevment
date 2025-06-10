import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
from playwright.sync_api import sync_playwright, Playwright
from dotenv import load_dotenv
import os
import time
import facebook_consts
import urllib.parse
import re
from sqlite_handler import SQLiteHandler
from pathlib import Path
load_dotenv()


sqlite = SQLiteHandler("./facebook/facebook_posts.db")
sqlite.setup_table("posts", {
    "id":"TEXT PRIMARY KEY",
    "entity": "TEXT",
    "user": "TEXT",
    "text": "TEXT",
    "likes": "INTEGER",
    "shares": "INTEGER",
    "coments": "INTEGER",
})

login_url = "https://www.facebook.com/?stype=lo&flo=1&deoia=1&jlou=AffX4q_FxaB7Pi0qDPvPz9A6n8yuGdPW3B6TkOl8Gi6NryNeejHkcKWGjcrUmkBNHf5c23Eqvs6XoOPM16oOc2BeBvohWesZj-EMwRh02g356g&smuh=28453&lh=Ac8IuLvOc7qLNLJa5Y4"
user = os.getenv("FB_EMAIL")
pwd = os.getenv("FB_PASSWORD")
all_posts = {
    "users": [],
    "posts_text": [],
    "likes": [],
    "shares": [],
    "coments": [],
    "raw_posts_text": []
}
busca = 'Renner'
tema = 'Roupas'
busca_quoted = urllib.parse.quote(busca + " " + tema)  
default_browser_path = os.getenv("OPERA_PATH")

browser_data_path = Path(__file__).parent / "browser_data"

def click_if_visible(element, timeout=2000):
    try:
        if element.is_visible(timeout=timeout):
            element.click()
            return True
        return False
    except:
        return False
    
def texto_para_numero(texto):
    texto = texto.strip().lower().replace(' ', '').replace(',', '.')
    if texto.endswith('mil'):
        return int(float(texto.replace('mil', '')) * 1000)
    elif texto.endswith('mi'):
        return int(float(texto.replace('mi', '')) * 1_000_000)
    elif texto.endswith('k'):
        return int(float(texto.replace('k', '')) * 1000)
    else:
        try:
            return int(texto)
        except ValueError:
            return 0

def process_facebook_post(raw_text):
    # 1. Remover quebras de linha
    cleaned = raw_text.replace('\n', '')

    # 2. Remover repetições como "Facebook"
    cleaned = re.sub(r'(Facebook)+', '', cleaned)

    # 3. Remover timestamps de vídeo, como "0:00 / 0:24"
    cleaned = re.sub(r'\d{1,2}:\d{2}\s*/\s*\d{1,2}:\d{2}', '', cleaned)

    # 4. Extrair nome do usuário antes de "·" ou "Seguir"
    match_user = re.search(r'([A-Z][^\n·]+?)\s*(?=·|Seguir)', cleaned)
    user_name = match_user.group(1).strip() if match_user else "Desconhecido"

    cleaned = re.sub(r'·[^·]*Seguir[^·]*·', '', cleaned)

    # 6. Extrair comentários
    match_comments = re.search(r'(\d{1,3}(?:[.,]\d+)?(?:\s*(mil|mi|k))?)\s*(comentário|comentários)', cleaned, re.IGNORECASE)
    comments = texto_para_numero(match_comments.group(1)) if match_comments else 0

    # 7. Compartilhamentos
    match_shares = re.search(r'(\d{1,3}(?:[.,]\d+)?(?:\s*(mil|mi|k))?)\s*(compartilhamento|compartilhamentos)', cleaned, re.IGNORECASE)
    shares = texto_para_numero(match_shares.group(1)) if match_shares else 0

    # 8. Reações
    match_reactions = re.search(r'Todas as reações:\s*(\d{1,3}(?:[.,]\d+)?(?:\s*(mil|mi|k))?)', cleaned, re.IGNORECASE)
    reactions = texto_para_numero(match_reactions.group(1)) if match_reactions else 0

    # 9. Extrair texto principal (entre nome e "Todas as reações:")
    post_body = ""
    if user_name in cleaned:
        body_start = cleaned.find(user_name) + len(user_name)
        body_end = cleaned.find("Todas as reações:")
        if body_end == -1:
            body_end = len(cleaned)
        post_body = cleaned[body_start:body_end]

        # Remover timestamps restantes (como "0:01", "12:43")
        post_body = re.sub(r'\b\d{1,2}:\d{2}\b', '', post_body)

        # Remover excesso de espaços
        post_body = re.sub(r'\s+', ' ', post_body).strip()

    return {
        "user": user_name,
        "coments": comments,
        "shares": shares,
        "likes": reactions,
        "text": post_body
    }

def run(playwright: Playwright):

    try:
        navegador = playwright.chromium.launch_persistent_context(user_data_dir=browser_data_path,  # pode ser outro diretório
            headless=True,
            executable_path=default_browser_path,)
        page = navegador.new_page()
        time.sleep(2)
        page.goto(login_url)
        for p in navegador.pages:
            if not p.url == 'https://v6.gxcorner.games/' and not 'facebook' in p.url : p.close()
        if not page.locator("input[placeholder='Pesquisar no Facebook']").is_visible():
            page.fill("input[name='email']", user)
            page.fill("input[name='pass']", pwd)
            page.click("button[name='login']")
            time.sleep(2)
            page.keyboard.press("Enter")
        if "two_step_verification" in page.url:
            input("Press Enter after completing two-step verification...")
        page.goto(f"https://www.facebook.com/search/posts/?q={busca_quoted}")
        while len(all_posts["posts_text"]) < 100:
            posts_visiveis = [post for post in page.locator("div[class='x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z']").all() if len(post.all_inner_texts()[0]) > 0]
            print("Posts adicionados:", len(all_posts["posts_text"]))
            for post in posts_visiveis:
                page.mouse.move(0,0)
                click_if_visible(post.locator("text=Ver mais"), timeout=1000)
                click_if_visible(post.locator("text=Ver original"), timeout=1000)
                post_texts = post.all_inner_texts()
                if not post_texts[0]:
                    page.mouse.move(page.viewport_size['width'] // 2, page.viewport_size['height'] // 2)
                    page.mouse.wheel(0, facebook_consts.POST_HEIGHT * 1)
                    continue
                post_dict = process_facebook_post(post_texts[0])

                if not (post_dict['text'] in all_posts["posts_text"]) and len(post_dict["text"]) > 0:
                    all_posts["users"].append(post_dict['user'])
                    all_posts["posts_text"].append(post_dict['text'])
                    all_posts["likes"].append(post_dict['likes'])
                    all_posts["shares"].append(post_dict['shares'])
                    all_posts["coments"].append(post_dict['coments'])
                    all_posts["raw_posts_text"].append(post_texts[0].replace("Facebook", "").replace("\n", ""))
            page.mouse.move(page.viewport_size['width'] // 2, page.viewport_size['height'] // 2)        
            page.mouse.wheel(0, facebook_consts.POST_HEIGHT * 1)   

        for i in range(len(all_posts["posts_text"])):
            post_info_dicts = {
                "id": sqlite.post_id(all_posts["posts_text"][i], all_posts["likes"][i], all_posts["coments"][i], all_posts["shares"][i]),
                "entity": busca,
                "user": all_posts["users"][i],
                "text": all_posts["posts_text"][i],
                "likes": all_posts["likes"][i],
                "shares": all_posts["shares"][i],
                "coments": all_posts["coments"][i],
                }
            sqlite.insert_data("posts", post_info_dicts)
            print(f"Post {i} adicionado ao banco de dados | ID: {post_info_dicts['id']}")
        print("Todos os posts foram adicionados ao banco de dados.")
        process_exit = True
    except Exception as e:
        process_exit = False
        print("Ocorreu um erro durante o scraping:")
        print(f"Erro: {e}")

    
    for p in navegador.pages:
        if p.url != "https://v6.gxcorner.games/" :p.close()
    navegador.close()
    sqlite.close()
    print("Navegador fechado.\nFinalizando scapping...")
    return process_exit

with sync_playwright() as playwright:
    times = 0
    while not run(playwright):
        times += 1
        print(f"Tentativa {times} falhou, tentando novamente...")
        time.sleep(5)
        if times > 3:
            print("Muitas tentativas falharam, encerrando o processo.")
            break
