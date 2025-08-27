import re
from enum import Enum

class Route(Enum):
    CHAT = "chat"
    AGENT = "agent"

# Palabras/indicadores que sugieren búsqueda/uso de herramientas
AGENT_HINTS = [
    r"\b(busca|investiga|averigua|encuentra|cítame|citas|fuentes|verifica|comprueba)\b",
    r"\b(últim[oa]s|hoy|reciente|actualizado|breaking)\b",
    r"\b(web|internet|sitio|página|press release|guidance|outlook|consenso)\b",
    r"\b(SES\.TO|TSX:|NYSE:|NASDAQ:|SEDAR\+|10-K|10-Q|MD&A)\b",
    r"\b(descarga|scrapea|scrapear|abre url|lee pdf)\b",
    r"\b(hazme un reporte|hazme un txt|hazme un md|genera archivo)\b",
]

def heuristic_route(user_msg: str) -> Route:
    text = user_msg.lower()
    signals = sum(bool(re.search(p, text)) for p in AGENT_HINTS)
    if signals >= 1:
        return Route.AGENT
    return Route.CHAT

# (Opcional) Router LLM si quieres mayor finura:
ROUTER_SYSTEM = """Eres un router. Responde SOLO con 'chat' o 'agent'.
'agent' si el usuario pide buscar en internet, fuentes, actualidad, verificación, o usar herramientas.
En todo lo demás: 'chat'."""

def llm_route(llm, user_msg: str) -> Route:
    out = llm.invoke(f"{ROUTER_SYSTEM}\nUsuario: {user_msg}\nRuta:")
    ans = str(out).strip().lower()
    return Route.AGENT if "agent" in ans else Route.CHAT

def decide_route(user_msg: str, llm=None, prefer_llm_router=False) -> Route:
    if prefer_llm_router and llm is not None:
        return llm_route(llm, user_msg)
    return heuristic_route(user_msg)
