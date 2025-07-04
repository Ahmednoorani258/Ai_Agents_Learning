from agents import Agent, Runner, trace
import agentops
from setupconfig import config
from dotenv import load_dotenv
import os

load_dotenv()
AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY") or "your-api-key"
agentops.init(AGENTOPS_API_KEY) 
async def main():
    # Initialize AgentOps
    agentops.init(
        api_key=AGENTOPS_API_KEY,
        default_tags=['openai agents sdk']
    )
    
    # Create an agent
    agent = Agent(
        name="Code Reviewer",
        instructions="Review code and suggest improvements."
    )

    # Create a trace for the code review workflow
    with trace("Code Review Workflow") as review_trace:
        # Run the agent (no need for 'with agentops()')
        result = await Runner.run(
            agent,
            "Review this code: def process_data(data): return data.strip()",
            run_config=config
        )
        
        # Log metrics
        # agentops.log_metric("code_complexity", "low")
        # agentops.log_metric("review_duration", 2.5)
        # agentops.log_metric("suggestions_count", 3)
        
        print(f"Review: {result.final_output}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())