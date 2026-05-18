from os import getenv
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY no está configurada en .env")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

def search_sports_news(query: str) -> dict:
    return tavily_client.search(
        query=query,
        include_answer=True,
        include_raw_content=False,
        max_results=5,
    )
