from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langgraph.store.memory import InMemoryStore
from contextlib import asynccontextmanager
from langmem import create_manage_memory_tool, create_search_memory_tool
from langmem_adapter import LangMemOpenAIAgentToolAdapter
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

store = InMemoryStore(
      index={
          "dims": 768,
          "embed": GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
      }
    )

@asynccontextmanager
async def get_store():
  yield store
  
namespace_template=("email_assistant", "{username}", "collection")


manage_adapter = LangMemOpenAIAgentToolAdapter(
    lambda store, namespace=None: create_manage_memory_tool(namespace=namespace, store=store),
    store_provider=get_store,
    namespace_template=namespace_template
)

# Initialize the search memory tool dynamically:
search_adapter = LangMemOpenAIAgentToolAdapter(
    lambda store, namespace=None: create_search_memory_tool(namespace=namespace, store=store),
    store_provider=get_store,
    namespace_template=namespace_template
)