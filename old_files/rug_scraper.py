from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import json

def scrape_rugs():
    with sync_playwright() as p:
        # 1. Launch a browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 2. Go to the URL and WAIT for the rug container to appear
        print("Visiting site...")
        page.goto("https://baseerorientalrugs.com/rugs-on-sale-today/ols/all")
        
        # Wait specifically for the GoDaddy store container to load
        page.wait_for_selector('[data-aid="PRODUCT_LIST_RENDERED"]')
        
        # 3. Get the fully rendered HTML
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Now find_all will actually see the rugs!
        cards = soup.find_all('div', {'data-aid': 'PRODUCT_LIST_RENDERED'})
        
        # ... rest of your extraction logic here ...
        
        print(f"Success! Found {len(cards)} rugs.")
        browser.close()

if __name__ == "__main__":
    scrape_rugs()