
import os
 
from agents.run import RunConfig
from dotenv import load_dotenv
import asyncio
from agents import Runner, ItemHelpers,function_tool

import os

from agents import (
    Agent,
    Runner,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
    AsyncOpenAI,
    OpenAIChatCompletionsModel
)

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")


# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

set_default_openai_client(client=external_client, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)


async def main():
    agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant.",
        model=model,
    )

    result = Runner.run_streamed(agent, input="Please tell me 5 jokes.")

    async for event in result.stream_events():
        if event.item.type == "message_output_item":
            print(ItemHelpers.text_message_output(event.item))

asyncio.run(main())