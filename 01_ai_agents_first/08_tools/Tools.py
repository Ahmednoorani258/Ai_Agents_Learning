# Tools let agents take actions: things like fetching data, running code, calling external APIs, and even using a computer. There are three classes of tools in the Agent SDK:

# Hosted tools: these run on LLM servers alongside the AI models. OpenAI offers retrieval, web search and computer use as hosted tools.
# Function calling: these allow you to use any Python function as a tool.
# Agents as tools: this allows you to use an agent as a tool, allowing Agents to call other agents without handing off to them.


import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, WebSearchTool, FileSearchTool,ComputerTool,CodeInterpreterTool,HostedMCPTool,ImageGenerationTool,LocalShellTool,FunctionTool, RunContextWrapper, function_tool
import asyncio
import json
from typing_extensions import TypedDict, Any

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta",
)
agent_model = OpenAIChatCompletionsModel(
    openai_client=external_client,
    model="gemini-2.0-flash",
)

config = RunConfig(
    model=agent_model,
    model_provider=external_client,
    tracing_disabled=True,
)


# agent = Agent(
#     name="Assistant",
#     tools=[
#         # Hosted tools
#         WebSearchTool(),
#         FileSearchTool(
#             max_num_results=3,
#             vector_store_ids=["VECTOR_STORE_ID"],
#         ),
#         # ComputerTool(computer="local"  ),
#         # CodeInterpreterTool(tool_config=config),
#         # # HostedMCPTool(on_approval_request="Please approve this action to continue."),
#         # ImageGenerationTool(tool_config=config),
#         # LocalShellTool(executor=config.model),
#     ],
# )

# async def main():
#     result = await Runner.run(agent, "Which coffee shop should I go to, taking into account my preferences and the weather today in SF?")
#     print(result.final_output) 
    
# if __name__ == "__main__":
#     asyncio.run(main())




# class Location(TypedDict):
#     lat: float
#     long: float

# @function_tool  # (1)!
# async def fetch_weather(location: Location) -> str:
#     # (2)!
#     """Fetch the weather for a given location.

#     Args:
#         location: The location to fetch the weather for.
#     """
#     # In real life, we'd fetch the weather from a weather API
#     return "sunny"


# @function_tool(name_override="fetch_data")  # (3)!
# def read_file(ctx: RunContextWrapper[Any], path: str, directory: str | None = None) -> str:
#     """Read the contents of a file.

#     Args:
#         path: The path to the file to read.
#         directory: The directory to read the file from.
#     """
#     # In real life, we'd read the file from the file system
#     return "<file contents>"


# agent = Agent(
#     name="Assistant",
#     tools=[fetch_weather, read_file],  # (4)!
# )

# for tool in agent.tools:
#     if isinstance(tool, FunctionTool):
#         print(tool.name)
#         print(tool.description)
#         print(json.dumps(tool.params_json_schema, indent=2))
#         print()



# from typing import Any

# from pydantic import BaseModel

# from agents import RunContextWrapper, FunctionTool



# def do_some_work(data: str) -> str:
#     return "done"


# class FunctionArgs(BaseModel):
#     username: str
#     age: int


# async def run_function(ctx: RunContextWrapper[Any], args: str) -> str:
#     parsed = FunctionArgs.model_validate_json(args)
#     return do_some_work(data=f"{parsed.username} is {parsed.age} years old")


# tool = FunctionTool(
#     name="process_user",
#     description="Processes extracted user data",
#     params_json_schema=FunctionArgs.model_json_schema(),
#     on_invoke_tool=run_function,
# )



# from agents import Agent, Runner
# import asyncio

# spanish_agent = Agent(
#     name="Spanish agent",
#     instructions="You translate the user's message to Spanish",
# )

# french_agent = Agent(
#     name="French agent",
#     instructions="You translate the user's message to French",
# )

# orchestrator_agent = Agent(
#     name="orchestrator_agent",
#     instructions=(
#         "You are a translation agent. You use the tools given to you to translate."
#         "If asked for multiple translations, you call the relevant tools."
#     ),
#     tools=[
#         spanish_agent.as_tool(
#             tool_name="translate_to_spanish",
#             tool_description="Translate the user's message to Spanish",
#         ),
#         french_agent.as_tool(
#             tool_name="translate_to_french",
#             tool_description="Translate the user's message to French",
#         ),
#     ],
# )

# async def main():
#     result = await Runner.run(orchestrator_agent, input="Say 'Hello, how are you?' in Spanish.", run_config=config)
#     print(result.final_output)
    

# if __name__ == "__main__":
#     asyncio.run(main())



async def extract_json_payload(run_result: RunResult) -> str:
    # Scan the agent’s outputs in reverse order until we find a JSON-like message from a tool call.
    for item in reversed(run_result.new_items):
        if isinstance(item, ToolCallOutputItem) and item.output.strip().startswith("{"):
            return item.output.strip()
    # Fallback to an empty JSON object if nothing was found
    return "{}"


# json_tool = data_agent.as_tool(
#     tool_name="get_data_json",
#     tool_description="Run the data agent and return only its JSON payload",
#     custom_output_extractor=extract_json_payload,
# )