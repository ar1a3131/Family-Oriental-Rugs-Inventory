import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time

def scrape_rugs():
    # GoDaddy OLS (Online Store) pagination uses the 'page' parameter
    base_url = "https://baseerorientalrugs.com/rugs-on-sale-today/ols/all?page="
    all_products = []
    
    # Looping through all 58 pages
    for page_num in range(1, 59):
        print(f"Processing page {page_num} of 58...")
        
        try:
            # Adding a User-Agent to avoid being flagged as a basic bot
            # a user-agent is a string of text that your browser/script sends
            # to a website's server every time you make a request. 
            # example: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36

            #When you use a library like Python's requests, the default User-Agent is usually something like python-requests/2.31.0.
            # that's why we have to disguise the request with a custom header, so that Go-Daddy doesn't see that it's python

            # **side note: You want to rotate identities: Advanced scrapers use a list of different User-Agents and pick a random one 
            # for every page. This is called User-Agent Rotation.**
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}


            # At its core, requests.get() is a function that sends an HTTP GET request to a specified URL and returns a 
            # Response object containing everything the server sent back (HTML, JSON, status codes, etc.).
            response = requests.get(base_url + str(page_num), headers=headers, timeout=15)

            # this "soup" variable takes a massive string of html and turns it
            # into a nested data structure that Python understands
            soup = BeautifulSoup(response.text, 'html.parser')
            print()
            
            # Using data-aid attributes identified from your HTML snippet
            cards = soup.find_all('div', {'data-aid': 'PRODUCT_CARD_RENDERED'})
            
            for card in cards:
                name_tag = card.find(attrs={"data-aid": "PRODUCT_CARD_NAME_RENDERED"})
                original_price_tag = card.find(attrs={"data-aid": "PRODUCT_PRICE_RENDERED"})
                price_tag = card.find(attrs={"data-aid": "PRODUCT_SALE_PRICE_RENDERED"})
                link_tag = card.find('a', href=True)
                img_tag = card.find('img')
                
                product = {
                    "name": name_tag.get_text(strip=True) if name_tag else "N/A",
                    "price": price_tag.get_text(strip=True) if price_tag else "N/A",
                    "original_price": original_price_tag.get_text(strip=True) if original_price_tag else "N/A",
                    "url": "https://baseerorientalrugs.com" + link_tag['href'] if link_tag else "N/A",
                    "image_url": img_tag['src'] if img_tag else "N/A"
                }
                all_products.append(product)
            
            # Wait 1.5 seconds between pages to stay under the radar
            time.sleep(1.5)
            
        except Exception as e:
            print(f"Error on page {page_num}: {e}")

    # 1. Save as JSON (Best for your React projects)
    with open('rug_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=4, ensure_ascii=False)

    # 2. Save as CSV (Best for Excel/Analysis)
    df = pd.DataFrame(all_products)
    df.to_csv('rug_data.csv', index=False, encoding='utf-8-sig')
    
    print(f"Success! {len(all_products)} rugs saved to rug_data.json and rug_data.csv")

if __name__ == "__main__":
    scrape_rugs()