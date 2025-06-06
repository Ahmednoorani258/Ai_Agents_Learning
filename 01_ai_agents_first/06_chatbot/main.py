import os
from dotenv import load_dotenv
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig


load_dotenv

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

@cl.on_chat_start
async def start():
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
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
    cl.user_session.set("chat_history", [])
    
    cl.user_session.set("config", config)
    agent = Agent(
        name="Assistant",
        instructions="Answer the user's questions to the best of your ability.",
        model=model,
    )
    
    cl.user_session.set("agent", agent)
    
    await cl.Message(content="Welcome to the Gemini-powered chatbot! How can I assist you today?").send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="thinking...")
    await msg.send()
    
    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    history = cl.user_session.get("chat_history", [])
    history.append({"role": "user", "content": message.content})
    # cl.user_session.set("chat_history", history)
    
    try:
        result = Runner.run_sync(
            starting_agent=agent,
            input=history,
            run_config=config,
        )
        
        response_content = result.final_output
        msg.content = response_content
        await msg.update()
        
        cl.user_session.set("chat_history", result.to_input_list())
        print(f"User: {message.content}")
        print(f"Assistant: {response_content}")
        
    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()
        print(f"Error: {str(e)}")


    