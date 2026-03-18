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

    for label, width, height in [
        ("Desktop 1440px", 1440, 900),
        ("Laptop  1280px", 1280, 800),
        ("Tablet   900px",  900, 700),
        ("Mobile   768px",  768, 1024),
        ("Mobile   390px",  390, 844),
        ("Mobile   320px",  320, 568),
    ]:
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(600)  # laisser les animations se lancer

        heading = page.locator("h1.hero-heading")
        em      = page.locator("h1.hero-heading em")

        # Bounding boxes
        page_width    = page.evaluate("window.innerWidth")
        heading_box   = heading.bounding_box()
        em_box        = em.bounding_box()

        # Le mot "standard" ne doit pas depasser le bord droit de la page
        em_right      = round(em_box["x"] + em_box["width"], 1)
        overflow      = em_right > page_width + 2   # +2px de tolerance

        print(f"\n== {label} (viewport={width}px) ==")
        print(f"   page width  : {page_width}px")
        print(f"   em right    : {em_right}px  (x={round(em_box['x'],1)} + w={round(em_box['width'],1)})")
        check(f"'un standard' dans le viewport ({em_right}px <= {page_width}px)", not overflow)

        # Screenshot annote
        slug = label.replace(" ", "_").replace("px", "").strip()
        shot = f"check_standard_{slug}.png"
        page.screenshot(path=shot, full_page=False)
        print(f"   [IMG] {shot}")

        page.close()

    browser.close()

total  = len(results)
passed = sum(1 for _, ok in results if ok)
failed = total - passed
print(f"\n{'='*48}")
print(f"  {passed}/{total} viewports OK", end="")
if failed:
    print(f"  -- {failed} probleme(s) detecte(s):")
    for label, ok in results:
        if not ok: print(f"    {FAIL} {label}")
else:
    print(" -- Aucun debordement detecte!")
print(f"{'='*48}\n")
sys.exit(0 if failed == 0 else 1)
