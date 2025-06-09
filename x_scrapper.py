from playwright.sync_api import sync_playwright
import time
import urllib.parse

# ❗️ Credenciais diretas
TW_USER = "larifdanadinha"
TW_EMAIL = "mariaebs@al.insper.edu.br"
TW_PASS = "InsperData2025"

# Entrada de busca
termo = input("🔎 Digite o termo de busca no Twitter: ")
termo_url = urllib.parse.quote(termo)
search_url = f"https://x.com/search?q={termo_url}&src=typed_query&f=live"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Login
    page.goto("https://x.com/login")
    page.wait_for_selector("input[name='text']")
    page.fill("input[name='text']", TW_USER)
    page.click("text='Next'")

    if page.is_visible("input[name='text']"):
        page.fill("input[name='text']", TW_EMAIL)
        page.click("text='Next'")

    # Verificação extra
    try:
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        # Preenche verificação extra (email/telefone)
        page.wait_for_selector("//input[@type='text' or @type='email']", timeout=10000)
        print("⚠️ Tela de verificação extra detectada!")

        verification_input = page.locator("//input[@type='text' or @type='email']")
        verification_input.wait_for(state="visible", timeout=5000)
        verification_input.click()
        page.wait_for_timeout(300)
        verification_input.fill(TW_EMAIL)
        page.click("text='Next'")

        # Espera o campo de senha e preenche logo em seguida
        page.wait_for_selector("//input[@type='password']", timeout=10000)
        password_input = page.locator("//input[@type='password']")
        password_input.click()
        page.wait_for_timeout(300)
        password_input.fill(TW_PASS)
        page.click("text='Log in'")

    except Exception as e:
        print("✅ Sem verificação extra.")
        print(f"(debug: {e})")

    if "challenge" in page.url or "verify" in page.url:
        input("⚠️ Verificação manual (captcha/SMS). Pressione Enter quando concluir...")


    page.wait_for_load_state("load")

    # Acessa busca
    page.goto(search_url)
    page.wait_for_timeout(5000)

    if "login" in page.url:
        print("❌ Redirecionado ao login.")
        page.screenshot(path="erro_login.png")
        exit()

    # Clica em "Latest"
    try:
        page.click("text=Latest")  # ou "Mais recentes" em português
        page.wait_for_timeout(3000)
    except Exception as e:
        print("⚠️ Aba 'Latest' não encontrada.")
        page.screenshot(path="erro_latest.png")
        raise e

    # Scroll para carregar mais tweets
    for _ in range(3):
        page.mouse.wheel(0, 2000)
        time.sleep(2)

    # Coleta os textos dos tweets
    tweets = page.query_selector_all("div[data-testid='tweetText']")
    print(f"\n{len(tweets)} tweets encontrados (exibindo até 10):")
    for i, tweet in enumerate(tweets[:10]):
        print(f"\nTweet {i+1}:\n{tweet.inner_text()}")

    browser.close()
