from models import Episode
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool,create_memory_manager
from langmem_adapter import LangMemOpenAIAgentToolAdapter
from contextlib import asynccontextmanager
from prompts import data, data_two,dataignore
import uuid
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY


manager = create_memory_manager(
    "google_genai:gemini-2.0-flash",
    schemas=[Episode],
    instructions="Extract examples of successful explanations, capturing the full chain of reasoning. Be concise in your explanations and precise in the logic of your reasoning.",
    enable_inserts=True,
)
     
store = InMemoryStore(
      index={
          "dims": 768,
          "embed": GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
      }
    )
store.put(
    ("email_assistant", "Junaid", "examples"),
    str(uuid.uuid4()),
    data
)
store.put(
    ("email_assistant", "Junaid", "examples"),
    str(uuid.uuid4()),
    data_two
)

   

store.put(
    ("email_assistant", "Junaid", "examples"),
    str(uuid.uuid4()),
    dataignore
)
@asynccontextmanager
async def get_store():
  yield store
  
namespace_template=("email_assistant", "{username}", "collection")
search_adapter = LangMemOpenAIAgentToolAdapter(
    lambda store, namespace=None: create_search_memory_tool(namespace=namespace, store=store),
    store_provider=get_store,
    namespace_template=namespace_template
)

manage_adapter = LangMemOpenAIAgentToolAdapter(
    lambda store, namespace=None: create_manage_memory_tool(namespace=namespace, store=store),
    store_provider=get_store,
    namespace_template=namespace_template
)