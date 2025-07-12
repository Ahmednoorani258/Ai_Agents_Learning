from agents import Agent
from tools import answer_from_knowledge_base

qa_agent = Agent(
    name="QA Agent",
    instructions="You are a helpful assistant. If the user asks a question, use your tools to find information in the knowledge base and answer with that information.",
    tools=[answer_from_knowledge_base],
)