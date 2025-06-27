import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, handoff
from agents.run import RunConfig
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client,
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,
)

billing_agent = Agent(
    name="Billing Agent",
    
    instructions="You handle all billing-related inquiries. Provide clear and concise information regarding billing issues."
)

# Agent specializing in refund processes
refund_agent = Agent(
    name="Refund Agent",
    instructions="You handle all refund-related processes. Assist users in processing refunds efficiently."
)

custom_handoff = handoff(
    agent=refund_agent,
    tool_name_override="custom_refund_handoff",
    tool_description_override="Handles refund processes with customized parameters."
)

# Triage agent that decides which specialist agent to hand off tasks to
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent should handle the user's request based on the nature of the inquiry.",
    handoffs=[billing_agent, refund_agent, custom_handoff],
    
)

async def main():
    user_input = "I need a refund for my recent purchase."
    result = await Runner.run(triage_agent, user_input, run_config=config)
    print(result.final_output)

asyncio.run(main())