from pydantic import BaseModel

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langgraph.store.memory import InMemoryStore

from langmem import create_memory_store_manager
from langmem import create_memory_manager
from pydantic import BaseModel
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file if present

config = {
    "GOOGLE_API_KEY": os.getenv("GEMINI_API_KEY"),
}
# Basic Config Values
MODEL = "google_genai:gemini-2.0-flash"

# preference_conversation = [
#     {"role": "user", "content": "I prefer dark mode in all my apps"},
#     {"role": "assistant", "content": "I'll remember that preference"},
# ]

# class PreferenceMemory(BaseModel):
#     """Store the user's preference"""
#     category: str
#     preference: str
#     context: str

# manager = create_memory_manager(
#     MODEL,
#     schemas=[PreferenceMemory]
# )

# async def main():
#     memories = await manager.ainvoke({"messages": preference_conversation})
#     print("\n[MEM]", memories, "\n")
#     print(memories[0][1])
            
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())





class PreferenceMemory(BaseModel):
    """Store preferences about the user."""
    category: str
    preference: str
    context: str

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")


store = InMemoryStore(
      index={
          "dims": 768,
          "embed": embeddings,
      }
    )

# Initialize memory manager with custom store
manager = create_memory_store_manager(
    MODEL,
    schemas=[PreferenceMemory],
    namespace=("AI-201", "{panaversity_user_id}"),
    store=store
)

async def run_example():

    # Simulate a conversation
    conversation = [
        {"role": "user", "content": "I prefer dark mode in all my apps"},
        {"role": "assistant", "content": "I'll remember that preference"}
    ]

    print("Process the conversation and store memories...")
    await manager.ainvoke(
        {"messages": conversation},
        config={"configurable": {"panaversity_user_id": "user123"}}
    )

    # Retrieve and display stored memories
    print("\nStored memories:")
    memories = store.search(("AI-201", "user123"))
    for memory in memories:
        print(f"\nMemory {memory.key}:")
        print(f"Content: {memory.value['content']}")
        print(f"Kind: {memory.value['kind']}")




print("\nStarting custom store example...\n")
asyncio.run(run_example())
print("\nExample completed.\n")