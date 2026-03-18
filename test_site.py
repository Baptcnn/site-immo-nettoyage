import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

HTML_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "index.html"))
URL = f"file:///{HTML_PATH.replace(os.sep, '/')}"

PASS = "[OK]"; FAIL = "[FAIL]"
results = []

def check(label, condition):
    status = PASS if condition else FAIL
    print(f"  {status} {label}")
    results.append((label, condition))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(URL)
    page.wait_for_load_state("networkidle")

    print("\n== DARK MODE (defaut) ==========================")
    theme = page.evaluate("document.documentElement.getAttribute('data-theme')")
    check("Pas de theme force au demarrage (dark par defaut)", theme != 'light')
    check("Bouton theme toggle present", page.locator("#themeToggle").is_visible())
    bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
    check("Background sombre en dark mode", bg not in ['rgb(255, 255, 255)', 'rgb(244, 241, 236)'])

    print("\n== LIGHT MODE TOGGLE ===========================")
    page.locator("#themeToggle").click()
    page.wait_for_timeout(500)
    theme_after = page.evaluate("document.documentElement.getAttribute('data-theme')")
    check("Attribut data-theme='light' apres clic", theme_after == 'light')
    bg_light = page.evaluate("getComputedStyle(document.body).backgroundColor")
    check("Background clair apres toggle", bg_light != bg)
    stored = page.evaluate("localStorage.getItem('ipn-theme')")
    check("Theme sauvegarde dans localStorage", stored == 'light')
    page.screenshot(path="screenshot_light.png", full_page=True)
    print("  [IMG] screenshot_light.png")

    print("\n== PERSISTANCE THEME ============================")
    page.reload()
    page.wait_for_load_state("networkidle")
    theme_reload = page.evaluate("document.documentElement.getAttribute('data-theme')")
    check("Theme light persiste apres rechargement", theme_reload == 'light')

    print("\n== RETOUR DARK MODE =============================")
    page.locator("#themeToggle").click()
    page.wait_for_timeout(500)
    theme_dark = page.evaluate("document.documentElement.getAttribute('data-theme')")
    check("Retour dark mode apres 2e clic", theme_dark == 'dark')
    page.screenshot(path="screenshot_dark.png", full_page=True)
    print("  [IMG] screenshot_dark.png")

    print("\n== SECTION LOCALISATION =========================")
    check("Section #localisation presente", page.locator("#localisation").is_visible())
    check("Lien 'Localisation' dans la nav", page.locator("nav a[href='#localisation']").is_visible())
    check("Iframe Google Maps presente", page.locator("#localisation iframe").count() > 0)
    check("Badge localisation present", page.locator(".map-pin-badge").is_visible())
    check("Adresse affichee (Barr)", "Barr" in page.locator("#localisation").inner_text())
    check("Lien Google Maps externe present", page.locator("#localisation a[target='_blank']").count() > 0)

    print("\n== CONTENU CORE =================================")
    check("Hero visible", page.locator("#accueil").is_visible())
    check("3 cartes de service", page.locator(".service-card").count() == 3)
    check("Section contact", page.locator("#contact").is_visible())
    check("Formulaire contact", page.locator("#contactForm").is_visible())
    check("Footer present", page.locator("footer").is_visible())

    print("\n== MOBILE (390px) ===============================")
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    check("Burger menu visible sur mobile", page.locator("#burger").is_visible())
    check("Bouton theme visible sur mobile", page.locator("#themeToggle").is_visible())
    page.screenshot(path="screenshot_mobile_new.png", full_page=True)
    print("  [IMG] screenshot_mobile_new.png")

    browser.close()

total = len(results)
passed = sum(1 for _, ok in results if ok)
failed = total - passed
print(f"\n{'='*48}")
print(f"  Resultats : {passed}/{total} tests", end="")
if failed:
    print(f"  ({failed} echec{'s' if failed > 1 else ''})")
    for label, ok in results:
        if not ok: print(f"    {FAIL} {label}")
else:
    print(" -- Tous les tests passent!")
print(f"{'='*48}\n")
sys.exit(0 if failed == 0 else 1)
