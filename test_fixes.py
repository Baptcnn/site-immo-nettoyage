import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

HTML_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "index.html"))
URL = f"file:///{HTML_PATH.replace(os.sep, '/')}"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # ── DESKTOP 1280px ─────────────────────────────
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)

    # Cartes services
    page.evaluate("window.scrollTo(0, document.getElementById('prestations').offsetTop)")
    page.wait_for_timeout(600)
    page.screenshot(path="fix_desktop_services.png")
    print("[IMG] fix_desktop_services.png")

    # Localisation
    page.evaluate("window.scrollTo(0, document.getElementById('localisation').offsetTop)")
    page.wait_for_timeout(400)
    page.screenshot(path="fix_desktop_localisation.png")
    print("[IMG] fix_desktop_localisation.png")

    page.close()

    # ── MOBILE 375px ───────────────────────────────
    page = browser.new_page(viewport={"width": 375, "height": 812})
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)

    # Hero + nav mobile
    page.screenshot(path="fix_mobile_hero.png")
    print("[IMG] fix_mobile_hero.png")

    # Stats bas de hero
    page.evaluate("window.scrollTo(0, 600)")
    page.wait_for_timeout(300)
    page.screenshot(path="fix_mobile_stats.png")
    print("[IMG] fix_mobile_stats.png")

    page.close()
    browser.close()

print("Done.")
