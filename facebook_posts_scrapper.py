from playwright.sync_api import sync_playwright, Playwright
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
load_dotenv()

login_url = "https://www.facebook.com/?stype=lo&flo=1&deoia=1&jlou=AffX4q_FxaB7Pi0qDPvPz9A6n8yuGdPW3B6TkOl8Gi6NryNeejHkcKWGjcrUmkBNHf5c23Eqvs6XoOPM16oOc2BeBvohWesZj-EMwRh02g356g&smuh=28453&lh=Ac8IuLvOc7qLNLJa5Y4"
user = os.getenv("FB_EMAIL")
pwd = os.getenv("FB_PASSWORD")

def run(playwright: Playwright):
    navegador = playwright.chromium.launch(headless=False)
    page = navegador.new_page()
    page.goto(login_url)
    page.fill("input[name='email']", user)
    page.fill("input[name='pass']", pwd)
    page.click("button[name='login']")
    page.mouse.click(page.viewport_size['width'] // 2, page.viewport_size['height'] // 2)
    page.fill("input[placeholder='Pesquisar no Facebook']", "Zara")
    page.keyboard.press("Enter")
    input("...")
    


with sync_playwright() as playwright:
    run(playwright)
