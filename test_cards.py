import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

HTML_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "index.html"))
URL = f"file:///{HTML_PATH.replace(os.sep, '/')}"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1200)

    # Forcer la visibilité des cartes + scroll
    page.evaluate("""
        document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
        document.querySelectorAll('.service-card').forEach(el => {
            el.style.opacity = '1';
            el.style.transform = 'none';
        });
        document.querySelector('.services-grid').scrollIntoView({block:'center'});
    """)
    page.wait_for_timeout(600)
    page.screenshot(path="fix_cards_zoom.png")
    print("[IMG] fix_cards_zoom.png")

    # Vérifier le texte et la taille de chaque nom de carte
    for i, card in enumerate(page.locator(".service-card").all()):
        name = card.locator(".service-name").inner_text()
        box  = card.locator(".service-name").bounding_box()
        lines = round(box["height"] / 30) if box else "?"
        print(f"  Carte {i+1}: '{name}' — hauteur={round(box['height'],1)}px (~{lines} ligne(s))")

    browser.close()
