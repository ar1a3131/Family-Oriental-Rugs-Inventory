import json
import os
import re
import csv
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright


def extract_image_url(card_root):
    """
    GoDaddy Websites+Marketing commerce cards paint the product photo on a
    NESTED div (data-ux="Background") inside [data-ux="CommerceCardPicture"].
    Check inline style first, then fall back to computed style.
    """
    return card_root.evaluate("""(el) => {
        const bgEl = el.querySelector('[data-ux="Background"]') || el;

        if (bgEl.style && bgEl.style.backgroundImage && bgEl.style.backgroundImage !== 'none') {
            return bgEl.style.backgroundImage.replace(/url\\(["']?(.*?)["']?\\)/i, '$1');
        }

        const bg = window.getComputedStyle(bgEl).backgroundImage;
        if (bg && bg !== 'none') {
            return bg.replace(/url\\(["']?(.*?)["']?\\)/i, '$1');
        }

        return null;
    }""")


def detect_total_pages(page):
    """
    Scrapes the maximum page number displayed in GoDaddy's pagination control.
    """
    try:
        page.wait_for_selector('[data-ux="GridCell"]', timeout=15000)
        page.mouse.wheel(0, 5000)
        page.wait_for_timeout(1500)

        max_page = page.evaluate("""() => {
            const container = document.querySelector('[data-ux="Pagination"]') || document;
            const elements = container.querySelectorAll('button, a, span, div');
            let max = 1;
            elements.forEach(el => {
                const text = el.textContent ? el.textContent.trim() : '';
                if (/^\\d+$/.test(text)) {
                    const num = parseInt(text, 10);
                    if (num > max && num < 500) {
                        max = num;
                    }
                }
            });
            return max;
        }""")
        return max_page
    except Exception as e:
        print(f"⚠️ Could not detect page count automatically (defaulting to 1): {e}")
        return 1


def run():
    # Save directly inside current project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, '../generated_data')
    os.makedirs(output_dir, exist_ok=True)

    base_catalog_url = "https://baseerorientalrugs.com/hand-kotted-rugs-sale-1/ols/products"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        all_rugs = []
        total_num_rugs = 1

        # 1. First Page & Detection
        print(f"🌐 Navigating to main catalog page to determine total pages...")
        page.goto(base_catalog_url, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        total_pages = detect_total_pages(page)
        print(f"📊 Detected {total_pages} pages in total.\n")

        # 2. Iterate through all pages
        for page_num in range(1, total_pages + 1):
            url = f"{base_catalog_url}?page={page_num}"
            print(f"📄 Scraping Page {page_num} of {total_pages} ({url})...")

            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                # Scroll down to ensure background images paint
                page.mouse.wheel(0, 4000)
                page.wait_for_timeout(2000)

                rug_elements = page.locator('[data-ux="GridCell"]').filter(
                    has=page.locator('[data-ux="CommerceCardTitle"]')
                ).all()

                if not rug_elements:
                    print(f"   ⚠️ No rugs found on page {page_num}.")

                for rug in rug_elements:
                    try:
                        name = rug.locator('[data-ux="CommerceCardTitle"] h4').first.inner_text().strip()

                        # Extract product URL
                        card_link = rug.locator('a[href*="/ols/products/"]').first
                        if card_link.count() == 0:
                            card_link = rug.locator('a').first

                        raw_href = card_link.get_attribute('href') if card_link.count() > 0 else None
                        product_url = urljoin("https://baseerorientalrugs.com", raw_href) if raw_href else "N/A"

                        # Price parsing
                        price_raw = rug.locator('[data-ux="CommerceCardPriceDisplay"]').first.inner_text().strip()
                        price_parts = price_raw.split()
                        original_price = price_parts[0] if len(price_parts) > 0 else "N/A"
                        sale_price = price_parts[1] if len(price_parts) > 1 else None

                        img_container = rug.locator('[data-ux="CommerceCardPicture"]').first
                        img_container.scroll_into_view_if_needed()

                        try:
                            page.wait_for_function(
                                """(el) => {
                                    const bg = el.querySelector('[data-ux="Background"]');
                                    return bg && bg.getAttribute('data-aid') &&
                                           bg.getAttribute('data-aid').startsWith('PRODUCT_IMAGE_RENDERED_');
                                }""",
                                arg=img_container.element_handle(),
                                timeout=4000
                            )
                        except Exception:
                            pass

                        img_url = extract_image_url(img_container) or "none"
                        if img_url != "none":
                            match = re.search(r'(https?://[^\s\'"\)]+)', img_url)
                            img_url = match.group(0) if match else "none"

                        all_rugs.append({
                            "id": total_num_rugs,
                            "name": name,
                            "product_url": product_url,
                            "original_price": original_price,
                            "sale_price": sale_price,
                            "image_url": img_url,
                            "source_page": page_num
                        })
                        total_num_rugs += 1
                    except Exception as inner_e:
                        print(f"      ⚠️ Skipping item {total_num_rugs}: {inner_e}")
                        continue

                print(f"   ✅ Scraped {len(rug_elements)} items from page {page_num}.")

            except Exception as outer_e:
                print(f"   ❌ Error loading page {page_num}: {outer_e}")
                continue

        # --- DEDUPLICATION ---
        seen_names = set()
        deduplicated_rugs = []
        for rug in all_rugs:
            if rug["name"] not in seen_names:
                seen_names.add(rug["name"])
                rug["id"] = len(deduplicated_rugs) + 1
                deduplicated_rugs.append(rug)

        # --- SAVE FILES ---
        json_output_path = os.path.join(output_dir, 'oriental_rugs.json')
        csv_output_path = os.path.join(output_dir, 'oriental_rugs.csv')

        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(deduplicated_rugs, f, indent=4, ensure_ascii=False)

        if deduplicated_rugs:
            keys = deduplicated_rugs[0].keys()
            with open(csv_output_path, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(deduplicated_rugs)

        print(f"\n✨ Done! Saved {len(deduplicated_rugs)} unique items across {total_pages} pages.")
        print(f"📁 Output files saved directly to:\n   - {json_output_path}\n   - {csv_output_path}")

        browser.close()


if __name__ == "__main__":
    run()