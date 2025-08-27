"""src/agents/research_agent.py
Agente híbrido (Chat ↔ ReAct con herramientas) usando Ollama + LangChain.
– Modo CHAT por defecto para conversación rápida (sin herramientas)
– Modo AGENTE (ReAct) cuando se detecta intención de buscar/verificar/citar
– REPL por defecto
"""

import argparse
import sys
import re
from enum import Enum

from langchain.agents import initialize_agent, AgentType

from src.config import get_local_llm
from src.tools.web_search import get_search_tool   # añade get_fetch_tool si lo usas
from src.prompts.research_prompts import RESEARCH_PREFIX
from src.tools.browser_login import browser_login
from src.tools.browser_goto import browser_goto

tools = [get_search_tool(), browser_login, browser_goto]

# ──────────────────────────────── ROUTER ────────────────────────────────
class Route(Enum):
    CHAT = "chat"
    AGENT = "agent"

AGENT_HINTS = [
    r"\b(busca|investiga|averigua|encuentra|cítame|citas|fuentes|verifica|comprueba)\b",
    r"\b(últim[oa]s|hoy|reciente|actualizado|breaking)\b",
    r"\b(web|internet|sitio|página|press release|guidance|outlook|consenso)\b",
    r"\b(SES\.TO|TSX:|NYSE:|NASDAQ:|SEDAR\+|10-K|10-Q|MD&A)\b",
    r"\b(descarga|scrapea|scrapear|abre url|lee pdf)\b",
    r"\b(hazme un reporte|hazme un txt|hazme un md|genera archivo)\b",
]

def decide_route(user_msg: str) -> Route:
    text = user_msg.lower()
    for p in AGENT_HINTS:
        if re.search(p, text):
            return Route.AGENT
    return Route.CHAT


# ─────────────────────────────── MODELOS ────────────────────────────────
# Puedes usar modelos distintos si tu config lo soporta
chat_llm  = get_local_llm()
agent_llm = chat_llm

# ─────────────────────────────── TOOLS ──────────────────────────────────
tools = [get_search_tool()]  # → añade aquí más tools si creas

# ─────────────────────────────── AGENTE (ReAct) ─────────────────────────
agent = initialize_agent(
    tools=tools,
    llm=agent_llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=4,
    early_stopping_method="generate",
    agent_kwargs={"prefix": RESEARCH_PREFIX},
)


# ─────────────────────────────── HANDLERS ───────────────────────────────
def handle_chat(query: str) -> str:
    """Modo chat directo sin herramientas."""
    prompt = f"Responde en español, breve y claro. Usuario: {query}"
    return str(chat_llm.invoke(prompt))

def handle_agent(query: str) -> str:
    """Modo agente ReAct con herramientas."""
    try:
        res = agent.invoke({"input": query})
        return res["output"] if isinstance(res, dict) and "output" in res else str(res)
    except Exception as e:
        # Fallback: una sola tirada “forzada” a Final Answer
        safe_prompt = (
            f"{RESEARCH_PREFIX}\n\n"
            "Thought: necesito responder con una sola búsqueda/razonamiento breve.\n"
            "Final Answer:\n"
            "- No pude completar el formato ReAct por un error de parseo.\n"
            "- A continuación intento responder con lo ya obtenido.\n"
            "- Si necesitas que rehaga con más detalle, dímelo.\n"
            "- \n"
            "- \n\n"
            "Fuentes:\n- "
        )
        try:
            return agent_llm.invoke(safe_prompt)
        except Exception:
            return f"Error del agente: {type(e).__name__}: {e}"


def smart_ask(query: str) -> str:
    """Decide ruta CHAT o AGENTE y responde."""
    route = decide_route(query)
    if route == Route.AGENT:
        return handle_agent(query)
    else:
        return handle_chat(query)


# ─────────────────────────────── CLI / REPL ─────────────────────────────
def main() -> None:
    p = argparse.ArgumentParser(description="Agente híbrido (Chat ↔ ReAct con tools).")
    g = p.add_mutually_exclusive_group()
    g.add_argument("-q", "--query", type=str, help="Pregunta directa.")
    g.add_argument("-f", "--file", type=str, help="Archivo de texto con la pregunta.")
    p.add_argument("-i", "--interactive", action="store_true", help="Modo interactivo (REPL).")
    args = p.parse_args()

    # ----- Query directa -----
    if args.query:
        print(smart_ask(args.query))
        return

    # ----- Desde archivo -----
    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            q = fh.read().strip()
        print(smart_ask(q))
        return

    # ----- REPL por defecto -----
    try:
        print("REPL (Ctrl+C para salir)\n")
        while True:
            q = input("> ").strip()
            if not q:
                continue
            print(smart_ask(q), end="\n\n")
    except (KeyboardInterrupt, EOFError):
        print("\nAdiós.")


if __name__ == "__main__":
    main()
