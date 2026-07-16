from playwright.sync_api import sync_playwright

#Claude generated this script to help me figure out
#the structure of the GoDaddy website HTML structure,
#because I was struggling to scrape the images/couldn't
#find the header/attribute that contains the image URLs

#very helpful

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # headed, so you can eyeball it
    page = browser.new_page()
    page.goto("https://baseerorientalrugs.com/oriental-rugs", timeout=60000)
    page.wait_for_timeout(5000)
    page.mouse.wheel(0, 4000)
    page.wait_for_timeout(3000)

    card = page.locator('[data-ux="CommerceCardPicture"]').first
    print("---- outerHTML ----")
    print(card.evaluate("el => el.outerHTML"))
    print("---- computed bg on el itself ----")
    print(card.evaluate("el => getComputedStyle(el).backgroundImage"))
    print("---- computed bg on ::before ----")
    print(card.evaluate("el => getComputedStyle(el, '::before').backgroundImage"))

    browser.close()