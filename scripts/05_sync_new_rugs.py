import json
import os
import re
import csv
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, 'generated_data')
JSON_PATH = os.path.join(DATA_DIR, 'oriental_rugs.json')
CSV_PATH = os.path.join(DATA_DIR, 'oriental_rugs.csv')
BASE_CATALOG_URL = "https://baseerorientalrugs.com/hand-kotted-rugs-sale-1/ols/products"


def load_existing_rugs():
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def extract_image_url(card_root):
    return card_root.evaluate("""(el) => {
        const bgEl = el.querySelector('[data-ux="Background"]') || el;
        if (bgEl.style && bgEl.style.backgroundImage && bgEl.style.backgroundImage !== 'none') {
            return bgEl.style.backgroundImage.replace(/url\\(["']?(.*?)["']?\\)/i, '$1');
        }
        const bg = window.getComputedStyle(bgEl).backgroundImage;
        return (bg && bg !== 'none') ? bg.replace(/url\\(["']?(.*?)["']?\\)/i, '$1') : null;
    }""")


def detect_total_pages(page):
    try:
        page.wait_for_selector('[data-ux="GridCell"]', timeout=10000)
        page.mouse.wheel(0, 5000)
        page.wait_for_timeout(1000)
        return page.evaluate("""() => {
            const container = document.querySelector('[data-ux="Pagination"]') || document;
            let max = 1;
            container.querySelectorAll('button, a, span, div').forEach(el => {
                const text = el.textContent ? el.textContent.trim() : '';
                if (/^\\d+$/.test(text)) {
                    const num = parseInt(text, 10);
                    if (num > max && num < 500) max = num;
                }
            });
            return max;
        }""")
    except Exception:
        return 1


def sync_new_rugs():
    existing_rugs = load_existing_rugs()
    # Build lookup set of all product URLs currently in oriental_rugs.json
    known_urls = {rug.get('product_url') for rug in existing_rugs if rug.get('product_url')}
    
    new_rugs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("🔍 Checking store for new rug additions...")
        page.goto(BASE_CATALOG_URL, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(2500)

        total_pages = detect_total_pages(page)

        for page_num in range(1, total_pages + 1):
            url = f"{BASE_CATALOG_URL}?page={page_num}"
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(1500)

            rug_elements = page.locator('[data-ux="GridCell"]').filter(
                has=page.locator('[data-ux="CommerceCardTitle"]')
            ).all()

            for rug in rug_elements:
                try:
                    card_link = rug.locator('a[href*="/ols/products/"]').first
                    if card_link.count() == 0:
                        card_link = rug.locator('a').first

                    raw_href = card_link.get_attribute('href') if card_link.count() > 0 else None
                    product_url = urljoin("https://baseerorientalrugs.com", raw_href) if raw_href else None

                    # If URL exists in oriental_rugs.json, skip it
                    if not product_url or product_url in known_urls:
                        continue

                    name = rug.locator('[data-ux="CommerceCardTitle"] h4').first.inner_text().strip()
                    price_raw = rug.locator('[data-ux="CommerceCardPriceDisplay"]').first.inner_text().strip()
                    price_parts = price_raw.split()
                    original_price = price_parts[0] if len(price_parts) > 0 else "N/A"
                    sale_price = price_parts[1] if len(price_parts) > 1 else None

                    img_container = rug.locator('[data-ux="CommerceCardPicture"]').first
                    img_container.scroll_into_view_if_needed()
                    img_url = extract_image_url(img_container) or "none"
                    if img_url != "none":
                        m = re.search(r'(https?://[^\s\'"\)]+)', img_url)
                        img_url = m.group(0) if m else "none"

                    record = {
                        "id": len(existing_rugs) + len(new_rugs) + 1,
                        "name": name,
                        "product_url": product_url,
                        "original_price": original_price,
                        "sale_price": sale_price,
                        "image_url": img_url,
                        "source_page": page_num
                    }

                    new_rugs.append(record)
                    known_urls.add(product_url)
                    print(f"   ➕ Found new rug: {name[:40]}...")

                except Exception:
                    continue

        browser.close()

    if not new_rugs:
        print("✨ No new rugs found. oriental_rugs.json is up to date.")
        return False

    print(f"✅ Added {len(new_rugs)} new rug(s) to oriental_rugs.json.")
    updated_dataset = existing_rugs + new_rugs

    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(updated_dataset, f, indent=4, ensure_ascii=False)

    if updated_dataset:
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=updated_dataset[0].keys())
            writer.writeheader()
            writer.writerows(updated_dataset)

    return True


if __name__ == "__main__":
    sync_new_rugs()