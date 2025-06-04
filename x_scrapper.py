from playwright.sync_api import sync_playwright
import time
import urllib.parse

# ❗️ Coloque seus dados aqui diretamente
TW_USER = "larifdanadinha"
TW_EMAIL = "mariaebs@al.insper.edu.br"
TW_PASS = "InsperData2025"

# Entrada da busca
termo = input("🔎 Digite o termo de busca no Twitter: ")
termo_url = urllib.parse.quote(termo)  # codifica para URL
search_url = f"https://x.com/search?q={termo_url}&src=typed_query&f=live"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Etapa 1: login
    page.goto("https://x.com/login")
    page.wait_for_selector("input[name='text']")
    page.fill("input[name='text']", TW_USER)
    page.click("text='Next'")

    # Etapa 2: email extra
    if page.is_visible("input[name='text']"):
        page.fill("input[name='text']", TW_EMAIL)
        page.click("text='Next'")

    # Etapa 3: verificação extra
    try:
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)
        page.wait_for_selector("//input[@type='text' or @type='email']", timeout=10000)
        print("Tela de verificação extra detectada!")
        verification_input = page.locator("//input[@type='text' or @type='email']")
        verification_input.wait_for(state="visible", timeout=5000)
        verification_input.click()
        page.wait_for_timeout(300)
        verification_input.fill(TW_EMAIL)
        page.click("text='Next'")
    except Exception as e:
        print("Sem verificação extra.")
        print(f"(debug: {e})")

    # Etapa 4: captcha/2FA
    if "challenge" in page.url or "verify" in page.url:
        input("Faça a verificação manual (captcha, SMS...) e pressione Enter...")

    # Etapa 5: senha
    try:
        page.wait_for_selector("//input[@type='password']")
        password_input = page.locator("//input[@type='password']")
        password_input.click()
        page.wait_for_timeout(300)
        password_input.fill(TW_PASS)
        page.click("text='Log in'")
    except Exception as e:
        print("❌ Erro ao preencher senha.")
        page.screenshot(path="erro_senha.png")
        raise e

    page.wait_for_load_state("load")

    # Etapa 6: busca
    page.goto(search_url)
    page.wait_for_timeout(5000)

    if "login" in page.url:
        print("❌ Algo deu errado, redirecionado ao login.")
        page.screenshot(path="erro_login.png")
        exit()

    # Etapa 7: espera tweets
    try:
        page.wait_for_selector("div[data-testid='tweet']", timeout=10000)
    except:
        print("⚠️ Nenhum tweet carregado.")
        page.screenshot(path="erro_tweet.png")
        browser.close()
        exit()

    # Scroll
    for _ in range(3):
        page.mouse.wheel(0, 2000)
        time.sleep(2)

    # Coleta
    tweets = page.query_selector_all("div[data-testid='tweet']")
    print(f"\n{len(tweets)} tweets carregados (mostrando até 10):")
    for i, tweet in enumerate(tweets[:10]):
        print(f"\nTweet {i+1}:\n{tweet.inner_text()}")

    browser.close()
