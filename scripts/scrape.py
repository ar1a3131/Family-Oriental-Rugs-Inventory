import json
import os
from playwright.sync_api import sync_playwright
import csv


def extract_image_url(card_root):
    """
    GoDaddy Websites+Marketing commerce cards paint the product photo on a
    NESTED div (data-ux="Background") inside [data-ux="CommerceCardPicture"],
    not on the CommerceCardPicture element itself. Check inline style first
    (fast, reliable), then fall back to computed style.
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
                page.wait_for_timeout(5000)  # Increased wait for Page 1 stability

                # Scroll is CRITICAL for background-image rendering
                page.mouse.wheel(0, 4000)
                page.wait_for_timeout(2000)

                rug_elements = page.locator('[data-ux="GridCell"]').filter(
                    has=page.locator('[data-ux="CommerceCardTitle"]')
                ).all()

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

                        # Make sure the card (and its lazy-loaded background image) is
                        # actually in view before we try to read it.
                        img_container.scroll_into_view_if_needed()

                        # Wait for GoDaddy's own "loaded" signal instead of a blind sleep:
                        # the nested Background div's data-aid flips to
                        # "PRODUCT_IMAGE_RENDERED_<name>" once the image is painted.
                        try:
                            page.wait_for_function(
                                """(el) => {
                                    const bg = el.querySelector('[data-ux="Background"]');
                                    return bg && bg.getAttribute('data-aid') &&
                                           bg.getAttribute('data-aid').startsWith('PRODUCT_IMAGE_RENDERED_');
                                }""",
                                arg=img_container.element_handle(),
                                timeout=5000
                            )
                        except Exception:
                            pass  # fall through and try to read whatever's there anyway

                        img_url = extract_image_url(img_container) or "none"

                        all_rugs.append({
                            "id": total_num_rugs,
                            "name": name,
                            "original_price": original_price,
                            "sale_price": sale_price,
                            "image_url": img_url,
                            "source_page": page_num
                        })
                        total_num_rugs += 1
                    except Exception as inner_e:
                        print(f"      ⚠️ Skipping rug {total_num_rugs} due to: {inner_e}")
                        continue

                print(f"   ✅ Collected {len(rug_elements)} rugs from this page.")

            except Exception as outer_e:
                print(f"   ❌ Error loading page {page_num}: {outer_e}")
                continue

        # --- DEDUPLICATION LOGIC ---
        seen_names = set()
        deduplicated_rugs = []
        
        for index, rug in enumerate(all_rugs, start=1):
            if rug["name"] not in seen_names:
                seen_names.add(rug["name"])
                # Re-index the IDs so they remain sequential (1, 2, 3...) after removing duplicates
                rug["id"] = len(deduplicated_rugs) + 1
                deduplicated_rugs.append(rug)

        # --- SAVE TO JSON ---
        output_path = '../generated_data/oriental_rugs.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            # Change all_rugs to deduplicated_rugs here:
            json.dump(deduplicated_rugs, f, indent=4, ensure_ascii=False)

        # --- SAVE TO CSV ---
        csv_output_path = '../generated_data/oriental_rugs.csv'
        if deduplicated_rugs:
            # Extract column headers from the keys of the first dictionary
            keys = deduplicated_rugs[0].keys()
            
            with open(csv_output_path, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()  # Writes 'id', 'name', 'original_price', etc.
                dict_writer.writerows(deduplicated_rugs)

        # Change the print statement to reflect the deduplicated count:
        print(f"\n✨ SUCCESS! Total rugs saved (duplicates removed): {len(deduplicated_rugs)}")
        print(f"Data saved to {output_path}")


        browser.close()


if __name__ == "__main__":
    run()