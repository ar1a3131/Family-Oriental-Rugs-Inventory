import json
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        all_rugs = []
        total_pages = 58  # You mentioned it goes up to 58
        total_num_rugs = 1
        for page_num in range(1, total_pages + 1):
            # Construct the URL for the specific page
            url = f"https://baseerorientalrugs.com/oriental-rugs/ols/products?page={page_num}"
            print(f"📄 Scraping Page {page_num} of {total_pages}...")
            

            try:
                page.goto(url, timeout=60000)
                # Wait for the grid to actually render
                page.wait_for_timeout(4000) 
                # Scroll to ensure background images trigger
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(1000)

                rug_elements = page.locator('[data-ux="GridCell"]').filter(has=page.locator('[data-ux="CommerceCardTitle"]')).all()


                for rug in rug_elements:
                    try:
                        
                        name = rug.locator('[data-ux="CommerceCardTitle"] h4').inner_text()
                        # 1. Price Splitting
                        price_raw = rug.locator('[data-ux="CommerceCardPriceDisplay"]').inner_text().strip()
                        price_parts = price_raw.split()
                        original_price = price_parts[0] if len(price_parts) > 0 else "N/A"
                        sale_price = price_parts[1] if len(price_parts) > 1 else None

                        # 2. Advanced Image Extraction (Using JavaScript Injection)
                        img_el = rug.locator('[role="img"]').first
                        # This JS snippet asks the browser for the 'background-image' property directly
                        img_src = page.evaluate(
                            "(el) => window.getComputedStyle(el).backgroundImage.replace(/url\\([\"']?|[\"']?\\)/g, '')", 
                            img_el.element_handle()
                        )

                        # 3. Clean up the URL (sometimes it's 'none')
                        if img_src == "none" or not img_src.startswith("http"):
                            img_src = None
                        
                        all_rugs.append({
                            "id": total_num_rugs,
                            "name": name.strip(),
                            "original price": original_price.strip(),
                            "sale price": sale_price.strip(),
                            "image_url": img_src,
                            "source_page": page_num
                        })
                        total_num_rugs += 1
                    except:
                        continue
                        
                print(f"   ✅ Collected {len(rug_elements)} rugs from this page.")

            except Exception as e:
                print(f"   ❌ Error loading page {page_num}: {e}")
                continue

        # --- SAVE TO JSON ---
        with open('oriental_rugs_full.json', 'w', encoding='utf-8') as f:
            json.dump(all_rugs, f, indent=4, ensure_ascii=False)
            
        print(f"\n✨ SUCCESS! Total rugs scraped: {len(all_rugs)}")
        print("Data saved to oriental_rugs_full.json")
        
        browser.close()

if __name__ == "__main__":
    run()