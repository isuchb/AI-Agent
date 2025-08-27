# src/tools/browser_goto.py
from langchain.tools import tool
from playwright.sync_api import sync_playwright
import os, json

DEFAULT_STATE_PATH = os.getenv("BROWSER_STATE_PATH", "data/storage_state.json")

@tool("browser_goto", return_direct=False)
def browser_goto(
    url: str,
    state_path: str = DEFAULT_STATE_PATH,
    wait_selector: str = "",
    headless: bool = True,
    screenshot_path: str = "",
) -> str:
    """
    Abre Chromium con la sesión guardada (storage_state.json) y navega a `url`.
    Opcionalmente espera un selector y hace captura.
    Devuelve JSON con ok, url y (si aplica) screenshot_path.
    """
    if not os.path.exists(state_path):
        return json.dumps({"ok": False, "error": f"state_path not found: {state_path}"})

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=state_path)
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        if wait_selector:
            try:
                page.wait_for_selector(wait_selector, timeout=8000)
            except Exception:
                pass
        if screenshot_path:
            os.makedirs(os.path.dirname(screenshot_path) or ".", exist_ok=True)
            page.screenshot(path=screenshot_path, full_page=True)
        current_url = page.url
        browser.close()
    return json.dumps({"ok": True, "url": current_url, "screenshot": screenshot_path or None})
