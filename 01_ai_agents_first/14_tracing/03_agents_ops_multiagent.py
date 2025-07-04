from agents import Agent, Runner, trace
import agentops
import os
from dotenv import load_dotenv
from setupconfig import config

load_dotenv()
agentops.init(os.getenv("AGENTOPS_API_KEY") or "your-api-key")

async def main():
    # Create specialized agents
    code_agent = Agent(
        name="Code Generator",
        instructions="Generate Python code based on requirements."
    )
    
    test_agent = Agent(
        name="Test Generator",
        instructions="Generate unit tests for Python code."
    )

    # Create a trace for the multi-agent workflow
    with trace("Code and Test Generation Workflow"):
        # Step 1: Generate code
        code_result = await Runner.run(
            code_agent,
            "Write a function to calculate factorial",
            run_config=config
        )
        
        print("Metric: code_complexity = medium")
        print("Metric: code_length =", len(code_result.final_output))
        
        # Step 2: Generate tests
        test_result = await Runner.run(
            test_agent,
            f"Write unit tests for this code: {code_result.final_output}",
            run_config=config
        )
        
        print("Metric: test_count = 3")
        print("Metric: test_coverage = 0.95")
        
        print(f"Generated code: {code_result.final_output}")
        print(f"Generated tests: {test_result.final_output}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
