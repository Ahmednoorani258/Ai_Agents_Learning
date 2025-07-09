import asyncio
from dotenv import load_dotenv
import os
from setupconfig import config
from langmem import create_memory_manager 
from pydantic import BaseModel
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

class Triple(BaseModel): #
    """Store all new facts, preferences, and relationships as triples."""
    subject: str
    predicate: str
    object: str
    context: str | None = None

# Configure extraction
manager = create_memory_manager(
    "google_genai:gemini-2.0-flash",
    schemas=[Triple],
    instructions="Extract user preferences and any other useful information",
    enable_inserts=True,
    enable_deletes=True,
)

conversation1 = [
    {"role": "user", "content": "We are building AI Agents to make Mars next humans stop"}
]
memories = manager.invoke({"messages": conversation1})
print("After first conversation:")
for m in memories:
    print(m)
    
conversation2 = [
    {"role": "user", "content": "Junaid AI Agents Workspace can now suggest designs for AI Agents Core."}
]
update = manager.invoke({"messages": conversation2, "existing": memories})
print("After second conversation:")
for m in update:
    print(m)

existing = [m for m in update if isinstance(m.content, Triple)]
     