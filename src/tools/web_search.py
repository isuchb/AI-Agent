# src/tools/web_search.py
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import Tool
from src.tools.utils import fetch_and_clean

def get_search_tool():
    return DuckDuckGoSearchRun()

def get_fetch_tool():
    return Tool(
        name="web_fetch",
        func=fetch_and_clean,
        description="Descarga y limpia el texto principal de una URL."
    )
