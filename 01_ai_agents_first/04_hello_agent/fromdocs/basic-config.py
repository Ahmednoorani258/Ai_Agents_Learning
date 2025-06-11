import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool,AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
import asyncio
from dataclasses import dataclass
from pydantic import BaseModel

# Load environment variables from .env file

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

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


@function_tool
def get_weather(location: str) -> str:
    return f"The weather in {location} is sunny."


agent = Agent(
    name="Weather Assistant",
    instructions="You are a helpful assistant that provides weather information.",
    tools=[get_weather]
)
# res = Runner.run_sync(agent, "What's the weather like in New York?", run_config=config)

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

agent2 = Agent(
    name="Calendar extractor",
    instructions="Extract calendar events from text",
    output_type=CalendarEvent,
)
# res = Runner.run_sync(agent2, "Schedule a meeting with John on 2023-10-01", run_config=config)
# ____________

# Handoffs
# ____________

booking_agent = Agent(
    name="Booking Agent",
    instructions="You are a helpful assistant that books appointments.",
)

refund_agent = Agent(
    name="Refund Agent",
    instructions="You are a helpful assistant that refunds appointments.",
)

triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "Help the user with their questions."
        "If they ask about booking, handoff to the booking agent."
        "If they ask about refunds, handoff to the refund agent."
    ),
    handoffs=[booking_agent, refund_agent]
)

# res = Runner.run_sync(triage_agent,"I want to book an appointment",run_config=config)

# @dataclass
# class UserContext:
#     uid: str
#     is_pro_user: bool

#     async def fetch_purchases() -> list[str]:
#         return ...

# agent = Agent[UserContext](
#     ...,
# )
# print(res.final_output)