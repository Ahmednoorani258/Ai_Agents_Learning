from agents import Agent, Runner

# Define individual agents
shopping_agent = Agent(
    name="Shopping Assistant",
    instructions="You assist users in finding products and making purchase decisions."
)

support_agent = Agent(
    name="Support Agent",
    instructions="You help users with post-purchase support and returns."
)

# Convert agents into tools
shopping_tool = shopping_agent.as_tool()
support_tool = support_agent.as_tool()

# Define a triage agent that delegates tasks
triage_agent = Agent(
    name="Triage Agent",
    instructions="You route user queries to the appropriate department.",
    tools=[shopping_tool, support_tool]
)

# Run the triage agent with a sample input
result = Runner.run_sync(triage_agent, "I need help with a recent purchase.")
print(result.final_output)