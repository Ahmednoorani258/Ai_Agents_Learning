import sys
import asyncio

# ✅ Fix for Windows + Psycopg + asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from setupconfig import config
import os
from dotenv import load_dotenv

from langmem import create_manage_memory_tool, create_search_memory_tool

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langgraph.store.postgres import AsyncPostgresStore

from contextlib import asynccontextmanager
from langgraph.store.postgres import AsyncPostgresStore
from langgraph.store.postgres.base import PoolConfig
from langmem_adapter import LangMemOpenAIAgentToolAdapter

import asyncio
from agents import Agent, Runner
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
conn_string = os.getenv("PG_URL")


@asynccontextmanager
async def get_store():
    async with AsyncPostgresStore.from_conn_string(
        conn_string,
        index={
            "dims": 768,
            "embed": GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        },
        pool_config=PoolConfig(
            min_size=5,
            max_size=20
        )
    ) as store:
        yield store
        
    # Run Once to setup and run Migrations

async def setup_store():
    async with get_store() as store:
        await store.setup()
    

namespace=("assistant", "collection")

agent_system_prompt_memory = """
< Role >
You are Junaids executive assistant. You are a top-notch executive assistant who cares about AI Agents and performing as well as possible.
 Role >

< Tools >
You have access to the following tools to help manage Junaid's communications and schedule:

1. manage_memory - Store any relevant information about contacts, actions, discussion, etc. in memory for future reference
2. search_memory - Search for any relevant information that may have been stored in memory
 Tools >

"""

# Initialize the manage memory tool dynamically:
manage_adapter = LangMemOpenAIAgentToolAdapter(
    lambda store, namespace=None: create_manage_memory_tool(namespace=namespace, store=store),
    store_provider=get_store,
    namespace_template=namespace
)
manage_memory_tool = manage_adapter.as_tool()

# Initialize the search memory tool dynamically:
search_adapter = LangMemOpenAIAgentToolAdapter(
    lambda store, namespace=None: create_search_memory_tool(namespace=namespace, store=store),
    store_provider=get_store,
    namespace_template=namespace
)
search_memory_tool = search_adapter.as_tool()

tools= [
    manage_memory_tool,
    search_memory_tool
]

agent = Agent(
    name="Assistant",
    instructions=agent_system_prompt_memory,
    tools=tools
)

async def run_example(message: str):
        
    result = await Runner.run(
        agent,
        message,
        run_config=config,
    )
    print(result.final_output)
    async with get_store() as store:
        res = await store.asearch(namespace)
        print("Memory Search Result:", res)

async def main():
    await setup_store()
    await run_example("So we are building Memory Layer for AI Agent")
    await run_example("Remember Ahmad is my Friend?")
    await run_example("Who are my friends and what am I building?")
    await run_example("It's not Ahmad who is my Friend instead Muhammad only?")
    await run_example("Do you know who is my friend?")
    
if __name__ == "__main__":
    asyncio.run(main())
