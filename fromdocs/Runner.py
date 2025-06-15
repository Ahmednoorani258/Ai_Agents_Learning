import random
from agents import Agent, Runner,ItemHelpers, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig,trace
import os
from dotenv import load_dotenv
import asyncio



load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

extrenal_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta",
)

model = OpenAIChatCompletionsModel(
    openai_client=extrenal_client,
    model="gemini-2.0-flash",
)

config = RunConfig(
    model=model,
    model_provider=extrenal_client,
    tracing_disabled=True,
)

# async def main():
#     agent = Agent(
#         name="Assistant",
#         instructions="Reply very concisely.",
#     )

#     with trace(workflow_name="conversation",group_id="1"):
#         # First turn
#         result = await Runner.run(agent, "What city is the Golden Gate Bridge in?")
#         print(result.final_output)
#         # San Francisco

#         # Second turn
#         new_input = result.to_input_list() + [{"role": "user", "content": "What state is it in?"}]
#         result = await Runner.run(agent, new_input)
#         print(result.final_output)
#         # California
#     # result = await Runner.run(agent, "What is the capital of France?", run_config=config)
#     # print(result.final_output)


@function_tool
def how_many_jokes() -> int:
    return random.randint(1, 10)


async def main():
    agent = Agent(
        name="Joker",
        instructions="First call the `how_many_jokes` tool, then tell that many jokes.",
        tools=[how_many_jokes],
        
    )

    result = Runner.run_streamed(
        agent,
        input="Hello",
        run_config=config,
    )
    print("=== Run starting ===")

    async for event in result.stream_events():
        # We'll ignore the raw responses event deltas
        if event.type == "raw_response_event":
            continue
        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        # When items are generated, print them
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print("-- Tool was called")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
            elif event.item.type == "message_output_item":
                print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
            else:
                pass  # Ignore other event types

    print("=== Run complete ===")


if __name__ == "__main__":
    asyncio.run(main())
