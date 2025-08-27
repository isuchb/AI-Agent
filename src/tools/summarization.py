from src.config import get_local_llm
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader

def summarize_pdf(path: str):
    llm = get_local_llm()
    docs = PyPDFLoader(path).load()
    chain = load_summarize_chain(llm, chain_type="map_reduce", verbose=False)
    return chain.run(docs)

if __name__ == "__main__":
    print(summarize_pdf("data/sample.pdf"))
