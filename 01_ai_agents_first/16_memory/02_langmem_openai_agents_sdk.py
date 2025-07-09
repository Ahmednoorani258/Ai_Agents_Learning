from setupconfig import config
from agents import set_tracing_disabled
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langgraph.store.memory import InMemoryStore
import os

import asyncio
from agents import Agent, Runner
from langmem import create_manage_memory_tool, create_search_memory_tool
from langmem_adapter import LangMemOpenAIAgentToolAdapter
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
set_tracing_disabled(disabled=False)

store = InMemoryStore(
      index={
          "dims": 768,
          "embed": GoogleGenerativeAIEmbeddings(model="models/text-embedding-004"),
          # "dims": 1536,
          # "embed": "openai:text-embedding-3-small",
      }
    )

namespace=("assistant", "collection")
print(store.search(namespace))

adapter = LangMemOpenAIAgentToolAdapter(create_manage_memory_tool(namespace=namespace,store=store))
call_manage_memory_tool = adapter.as_tool()

search_memory_tool_adapter = LangMemOpenAIAgentToolAdapter(create_search_memory_tool(namespace=namespace,store=store))
call_search_memory_tool = search_memory_tool_adapter.as_tool()

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

agent = Agent(
    name="Assistant",
    instructions=agent_system_prompt_memory,
    tools=[call_manage_memory_tool, call_search_memory_tool],
)

async def run_example(message: str):

    result = await Runner.run(
        agent,
        message,
        run_config=config,
    )
    print(result.final_output)


asyncio.run(run_example("Ahmad is my friend"))
print(store.search(namespace))
asyncio.run(run_example("Who are my friends"))
print(store.search(namespace))
asyncio.run(run_example("Oh no I meant Muhammad Ahmad not Ahmad is my Friend. Update it without asking any Qs"))
print(store.search(namespace))
asyncio.run(run_example("Who are my friends"))
print(store.search(namespace))
asyncio.run(run_example("Sir Zia Ullah Khan is my Mentor"))
print(store.search(namespace))

asyncio.run(run_example("Who is my Mentor?"))
print(store.search(namespace))