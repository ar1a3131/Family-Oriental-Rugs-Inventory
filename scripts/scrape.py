import json
import os
from playwright.sync_api import sync_playwright

def run():
    # Ensure the output directory exists
    os.makedirs('../generated_data', exist_ok=True)

    with sync_playwright() as p:
        # Suggestion: headless=False if you want to watch the first 2 pages
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        all_rugs = []
        total_pages = 58 
        total_num_rugs = 1

        for page_num in range(1, total_pages + 1):
            # URL Check: Often Page 1 is just the base URL
            if page_num == 1:
                url = "https://baseerorientalrugs.com/oriental-rugs"
            else:
                url = f"https://baseerorientalrugs.com/oriental-rugs/ols/products?page={page_num}"
            
            print(f"📄 Scraping Page {page_num} of {total_pages}...")

            try:
                page.goto(url, timeout=60000)
                page.wait_for_timeout(5000) # Increased wait for Page 1 stability
                
                # Scroll is CRITICAL for background-image rendering
                page.mouse.wheel(0, 4000)
                page.wait_for_timeout(2000)

                rug_elements = page.locator('[data-ux="GridCell"]').filter(has=page.locator('[data-ux="CommerceCardTitle"]')).all()

                if not rug_elements:
                    print(f"   ⚠️ No rugs found on page {page_num}. Check if the URL is correct.")

                for rug in rug_elements:
                    try:
                        name = rug.locator('[data-ux="CommerceCardTitle"] h4').first.inner_text().strip()

                        # Price Splitting
                        price_raw = rug.locator('[data-ux="CommerceCardPriceDisplay"]').first.inner_text().strip()
                        price_parts = price_raw.split()
                        original_price = price_parts[0] if len(price_parts) > 0 else "N/A"
                        sale_price = price_parts[1] if len(price_parts) > 1 else None

                        img_container = rug.locator('[data-ux="CommerceCardPicture"]').first

                        # JS Pseudo-element extraction
                        img_url = page.evaluate("""(el) => {
                            const style = window.getComputedStyle(el, '::before');
                            const bi = style.getPropertyValue('background-image');
                            return bi.replace(/url\\(['"]?(.*?)['"]?\\)/i, '$1');
                        }""", img_container.element_handle())

                        if not img_url or img_url == "none":
                            img_url = page.evaluate("(el) => window.getComputedStyle(el).backgroundImage.replace(/url\\([\"']?|[\"']?\\)/g, '')", img_container.element_handle())
                                                
                        all_rugs.append({
                            "id": total_num_rugs,
                            "name": name,
                            "original_price": original_price,
                            "sale_price": sale_price,
                            "image_url": img_url,
                            "source_page": page_num
                        })
                        total_num_rugs += 1
                    except Exception as inner_e: # <--- FIXED: Added 'as inner_e'
                        print(f"      ⚠️ Skipping rug {total_num_rugs} due to: {inner_e}")
                        continue
                        
                print(f"   ✅ Collected {len(rug_elements)} rugs from this page.")

            except Exception as outer_e: # <--- FIXED: Already had 'as e', but kept consistent
                print(f"   ❌ Error loading page {page_num}: {outer_e}")
                continue

        # --- SAVE TO JSON ---
        output_path = '../generated_data/oriental_rugs_full.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_rugs, f, indent=4, ensure_ascii=False)
            
        print(f"\n✨ SUCCESS! Total rugs scraped: {len(all_rugs)}")
        print(f"Data saved to {output_path}")

        browser.close()

if __name__ == "__main__":
    run()