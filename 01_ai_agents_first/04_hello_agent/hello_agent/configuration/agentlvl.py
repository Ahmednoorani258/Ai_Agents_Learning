import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta",
)

set_tracing_disabled(disabled=True)


async def main():
    agent = Agent(
        name="Assistant",
        instructions="Your name is Assistant. You are a helpful assistant.",
        model=OpenAIChatCompletionsModel(
            openai_client=client,
            model="gemini-2.0-flash",
        ),
    )
    result = await Runner.run(
        agent,
        input="Hello, what is your name?",
    )
    
    print(result.final_output)
    
if __name__ == "__main__":
    asyncio.run(main())