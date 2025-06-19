import asyncio
from dataclasses import dataclass
from agents import Agent, AsyncOpenAI,OpenAIChatCompletionsModel,RunConfig ,RunContextWrapper, Runner, function_tool
import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
  
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
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

@dataclass
class UserInfo1:
    name: str
    uid: int
    location: str = "Pakistan"

@function_tool
async def fetch_user_age(wrapper: RunContextWrapper[UserInfo1]) -> str:
    '''Returns the age of the user.'''
    return f"User {wrapper.context.name} is 30 years old"

@function_tool
async def fetch_user_location(wrapper: RunContextWrapper[UserInfo1]) -> str:
    '''Returns the location of the user.'''
    return f"User {wrapper.context.name} is from {wrapper.context.location}"

async def main():
    user_info = UserInfo1(name="Muhammad Qasim", uid=123)

    agent = Agent[UserInfo1](
        name="Assistant",
        tools=[fetch_user_age,fetch_user_location],
        model=model
    )

    result = await Runner.run(
        starting_agent=agent,
        input="What is the age of the user? current location of his/her?",
        context=user_info,
        run_config=config
    )

    print(result.final_output)
    # The user John is 47 years old.

if __name__ == "__main__":
    asyncio.run(main())