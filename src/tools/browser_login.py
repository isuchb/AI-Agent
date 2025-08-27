# src/tools/browser_login.py
from typing import Optional, Dict
from langchain.tools import tool
from playwright.sync_api import sync_playwright
import json
import os
import time

DEFAULT_STATE_PATH = os.getenv("BROWSER_STATE_PATH", "data/storage_state.json")

def _ensure_dir(path: str):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

@tool("browser_login", return_direct=False)
def browser_login(
    url: str,
    username_selector: str,
    password_selector: str,
    submit_selector: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    wait_selector_after_login: Optional[str] = None,
    state_path: str = DEFAULT_STATE_PATH,
    headless: bool = True,
    extra_wait_ms: int = 1500,
) -> str:
    """
    Abre Chromium, navega a `url`, rellena usuario/contraseña y hace click en submit.
    Guarda cookies/session en `state_path` (para reusar sin loguear otra vez).
    Devuelve un pequeño JSON con estado final.

    Parámetros:
    - url: URL de login
    - username_selector: selector CSS del input de usuario
    - password_selector: selector CSS del input de contraseña
    - submit_selector: selector CSS del botón de submit
    - username/password: si no se pasan, se cogen de variables de entorno:
        LOGIN_USER / LOGIN_PASS
    - wait_selector_after_login: CSS que indica que el login fue correcto (ej. un avatar/menú)
    - state_path: ruta para guardar cookies y storage (default data/storage_state.json)
    - headless: True/False (útil para debug visual)
    - extra_wait_ms: espera adicional tras el submit
    """
    user = username or os.getenv("LOGIN_USER")
    pwd  = password or os.getenv("LOGIN_PASS")
    if not user or not pwd:
        return json.dumps({"ok": False, "error": "Missing credentials (LOGIN_USER/LOGIN_PASS or params)"})

    _ensure_dir(state_path)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()  # arranca limpio
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")

        # Rellenar credenciales
        page.fill(username_selector, user)
        page.fill(password_selector, pwd)

        # Enviar
        page.click(submit_selector)

        # Espera básica
        time.sleep(max(0, extra_wait_ms) / 1000.0)

        # Si proporcionas un selector que solo aparece logueado, espera por él
        ok = True
        if wait_selector_after_login:
            try:
                page.wait_for_selector(wait_selector_after_login, timeout=8000)
            except Exception:
                ok = False

        # Guarda estado
        context.storage_state(path=state_path)

        # Info útil de vuelta
        current_url = page.url
        browser.close()

    return json.dumps({"ok": ok, "state_path": state_path, "url": current_url})
