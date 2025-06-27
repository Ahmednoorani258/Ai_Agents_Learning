import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, RunConfig
import os
from dotenv import load_dotenv
from pydantic import BaseModel

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


class WeatherAnswer(BaseModel):
  location: str
  temperature_c: float
  summary: str
  

agent = Agent(
  name="StructuredWeatherAgent",
  instructions="Use the final_output tool with WeatherAnswer schema.",
  output_type=WeatherAnswer
)

async def main():
    runner = await Runner.run(agent, input="What is the current weather in San Francisco?", run_config=config)
    print(runner.final_output)
    print(type(runner.final_output))
# 
    print(runner.final_output.temperature_c)
    return runner.final_output.temperature_c

if __name__ == "__main__":
    asyncio.run(main())