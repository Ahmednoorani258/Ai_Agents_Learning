from agents import Agent, Runner, trace
from agentops import AgentOps

async def main():
    # Initialize AgentOps
    agentops = AgentOps()
    
    # Create an agent
    agent = Agent(
        name="Code Reviewer",
        instructions="Review code and suggest improvements."
    )

    # Create a trace for the code review workflow
    with trace("Code Review Workflow") as review_trace:
        # Start monitoring the agent
        with agentops.monitor():
            # Run the agent
            result = await Runner.run(
                agent,
                "Review this code: def process_data(data): return data.strip()"
            )
            
            # Log metrics
            agentops.log_metric("code_complexity", "low")
            agentops.log_metric("review_duration", 2.5)
            agentops.log_metric("suggestions_count", 3)
            
            print(f"Review: {result.final_output}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())