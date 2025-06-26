# Import standard libraries
import os
import asyncio
from dataclasses import dataclass

# Import environment variable loader
from dotenv import load_dotenv

# Import required classes and functions from Agents SDK
from agents import (
    Agent, Runner, function_tool,
    AsyncOpenAI, OpenAIChatCompletionsModel,
    RunConfig, handoff, RunContextWrapper
)

# Import handoff input filters
from agents.extensions import handoff_filters
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX  # Recommended prompt prefix

# Pydantic for validating input schema from LLM
from pydantic import BaseModel

# ✅ Step 1: Load environment variables (e.g. API keys)
load_dotenv()

# ✅ Step 2: Get Gemini API Key from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# ✅ Step 3: Create an external OpenAI-compatible client for Gemini API
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta",  # Gemini-compatible endpoint
)

# ✅ Step 4: Define the model that uses the external Gemini client
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",  # Gemini model name
    openai_client=external_client,
)

# ✅ Step 5: Configure run settings for the agent runtime
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,  # Disable tracing (you can enable for debugging)
)

# ✅ Step 6: Define agents
billing_agent = Agent(name="Billing agent")
refund_agent = Agent(name="Refund agent")

# ✅ Step 7: Define triage agent that can handoff to billing or refund agents
triage_agent = Agent(
    name="Triage agent",
    handoffs=[
        billing_agent,  # Direct agent handoff (default tool name: transfer_to_billing_agent)
        handoff(refund_agent)  # Customizable handoff to refund agent
    ]
)

# ✅ Step 8: Define a simple handoff callback that runs when handoff happens
def on_handoff(ctx: RunContextWrapper[None]):
    print("Handoff called")  # Could be used for logging, data fetching, etc.

# ✅ Step 9: Define a data model to take input from LLM when triggering a handoff
class EscalationData(BaseModel):
    reason: str  # LLM must provide this when calling the handoff tool

# ✅ Step 10: Create a standalone agent and define a customizable handoff to it
agent = Agent(name="My agent")
handoff_obj = handoff(
    agent=agent,
    tool_name_override="custom_handoff_tool",  # Custom name for the tool
    tool_description_override="Custom description",  # Custom description for LLM's understanding
    on_handoff=on_handoff,  # Callback when handoff is called
    input_type=EscalationData,  # Schema LLM must follow
    input_filter=handoff_filters.remove_all_tools,  # Strip tool call history from conversation
)

# ✅ Step 11: Use recommended prompt prefix for better LLM behavior around handoffs
billing_agent = Agent(
    name="Billing agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    <Fill in the rest of your prompt here>.""",  # Complete with your billing-specific logic
)
