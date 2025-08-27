import pandas as pd
from langchain_experimental.agents.agent_toolkits.pandas.base import create_pandas_dataframe_agent
from src.config import get_local_llm

def analyze_csv(csv_path: str, query: str):
    df = pd.read_csv(csv_path)
    agent = create_pandas_dataframe_agent(get_local_llm(), df, verbose=True)
    return agent.run(query)

if __name__ == "__main__":
    print(analyze_csv("data/sample.csv", "¿Cuántas filas tiene este dataset?"))
