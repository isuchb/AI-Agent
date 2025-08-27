"""src/agents/research_agent.py
Agente web local (Ollama + LangChain) con CLI dinámico.
– Busca en Internet – Resume – Devuelve 3-5 fuentes
"""

import argparse
import sys

from langchain.agents import initialize_agent, AgentType

from src.config import get_local_llm
from src.tools.web_search import get_search_tool   # añade get_fetch_tool si lo usas
from src.prompts.research_prompts import RESEARCH_PREFIX

# ─────────────────────────────────────────  MODELO  ──────────────────────────────────────────
llm = get_local_llm()

# ──────────────────────────────────────────  TOOLS  ──────────────────────────────────────────
tools = [get_search_tool()]  # → pon aquí get_fetch_tool() si lo creaste

# ─────────────────────────────────────────  AGENTE  ──────────────────────────────────────────

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # ← clave
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=4,
    early_stopping_method="generate",
    agent_kwargs={"prefix": RESEARCH_PREFIX},
)


# ──────────────────────────────────  FUNCIÓN PRINCIPAL  ──────────────────────────────────────
def ask_web(query: str) -> str:
    try:
        res = agent.invoke({"input": query})
        return res["output"] if isinstance(res, dict) and "output" in res else str(res)
    except Exception as e:
        # Fallback: una sola tirada “forzada” a Final Answer
        safe_prompt = (
            f"{RESEARCH_PREFIX}\n\n"
            "Thought: necesito responder con una sola búsqueda/razonamiento breve.\n"
            "Assumption: ninguna\n"
            "Final Answer:\n"
            "- No pude completar el formato ReAct por un error de parseo.\n"
            "- A continuación intento responder con lo ya obtenido.\n"
            "- Si necesitas que rehaga con más detalle, dímelo.\n"
            "- \n"
            "- \n\n"
            "Fuentes:\n- "
        )
        try:
            return llm.invoke(safe_prompt)
        except Exception:
            return f"Error del agente: {type(e).__name__}: {e}"



# ───────────────────────────────────────────  CLI  ───────────────────────────────────────────
def main() -> None:
    p = argparse.ArgumentParser(description="Agente ReAct local para búsquedas web y resúmenes.")
    g = p.add_mutually_exclusive_group()
    g.add_argument("-q", "--query", type=str, help="Pregunta a realizar al agente.")
    g.add_argument("-f", "--file", type=str, help="Archivo de texto con la pregunta.")
    p.add_argument("-i", "--interactive", action="store_true", help="Modo interactivo (REPL).")
    p.add_argument("--iters", type=int, default=4, help="Máx. iteraciones del agente (por defecto 4).")
    args = p.parse_args()

    # Ajustar iteraciones si el usuario cambia el valor
    if args.iters != agent.max_iterations:
        agent.max_iterations = args.iters  # type: ignore

    # ----- REPL -----
    if args.interactive:
        try:
            print("REPL (Ctrl+C para salir)\n")
            while True:
                q = input("> ").strip()
                if not q:
                    continue
                print(ask_web(q), end="\n\n")
        except (KeyboardInterrupt, EOFError):
            print("\nAdiós.")
        return

    # ----- Query directa -----
    if args.query:
        print(ask_web(args.query))
        return

    # ----- Leer pregunta desde archivo -----
    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            q = fh.read().strip()
        print(ask_web(q))
        return

    # ----- Leer de stdin o pedir input -----
    try:
        print("REPL (Ctrl+C para salir)\n")
        while True:
            q = input("> ").strip()
            if not q:
                continue
            print(ask_web(q), end="\n\n")
    except (KeyboardInterrupt, EOFError):
        print("\nAdiós.")

if __name__ == "__main__":
    main()
