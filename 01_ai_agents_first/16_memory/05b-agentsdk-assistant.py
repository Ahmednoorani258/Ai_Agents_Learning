from pydantic import BaseModel, Field
from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig,
    function_tool
)
from typing import Dict, Any
from typing_extensions import TypedDict, Literal, Annotated
from setupconfig import config
import asyncio

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langgraph.store.memory import InMemoryStore
from contextlib import asynccontextmanager
from langmem import create_manage_memory_tool, create_search_memory_tool
from langmem_adapter import LangMemOpenAIAgentToolAdapter  # import from your package

import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY


profile = {
    "name": "Ahmed",
    "full_name": "Muhammad Ahmed Noornai",
    "user_profile_background": "AI Products Manager Building My AI Agents Workforce.",
}

prompt_instructions = {
    "triage_rules": {
        "ignore": "Marketing newsletters, spam emails, mass company announcements",
        "notify": "Team member out sick, build system notifications, project status updates",
        "respond": "Direct questions from team members, meeting requests, critical bug reports",
    },
    "agent_instructions": "Use these tools when appropriate to help manage Junaid's tasks efficiently."
}

# Example incoming email
email = {
    "from": "Alice Smith ",
    "to": "Muhammad Ahmed Noorani",
    "subject": "Quick question about API documentation",
    "body": """
Hi Junaid,

I was reviewing the API documentation for the new authentication service and noticed a few endpoints seem to be missing from the specs. Could you help clarify if this was intentional or if we should update the docs?

Specifically, I'm looking at:
- /auth/refresh
- /auth/validate

Thanks!
Alice""",
}

class Email(BaseModel):
    from_: str = Field(alias="from")
    to: str
    subject: str
    body: str

email_model = Email(**email)
# print(email_model.model_dump_json(by_alias=True))
class Router(BaseModel):
    """Analyze the unread email and route it according to its content."""

    reasoning: str = Field(
        description="Step-by-step reasoning behind the classification."
    )
    classification: Literal["ignore", "respond", "notify"] = Field(
        description="The classification of an email: 'ignore' for irrelevant emails, "
        "'notify' for important information that doesn't need a response, "
        "'respond' for emails that need a reply",
    )
    
# Triage system prompt template
triage_system_prompt_template = """
< Role >
You are {full_name}'s executive assistant. You are a top-notch executive assistant who cares about {name} performing as well as possible.
 Role >

< Background >
{user_profile_background}.
 Background >

< Instructions >

{name} gets lots of emails. Your job is to categorize each email into one of three categories:

1. IGNORE - Emails that are not worth responding to or tracking
2. NOTIFY - Important information that {name} should know about but doesn't require a response
3. RESPOND - Emails that need a direct response from {name}

Classify the below email into one of these categories.

 Instructions >

< Rules >
Emails that are not worth responding to:
{triage_no}

There are also other things that {name} should know about, but don't require an email response. For these, you should notify {name} (using the `notify` response). Examples of this include:
{triage_notify}

Emails that are worth responding to:
{triage_email}
 Rules >

< Few shot examples >
{examples}
 Few shot examples >
"""

# Triage User Prompt Template
triage_user_prompt_template = """
Please determine how to handle the below email thread:

From: {author}
To: {to}
Subject: {subject}
{email_thread}"""

def create_prompt(template: str, variables: Dict[str, any]) -> str:
    """Creates a prompt using an f-string and a dictionary of variables."""
    try:
        return template.format(**variables)
    except KeyError as e:
        return f"Error: Missing variable '{e.args[0]}' in the provided dictionary."
     
system_prompt = create_prompt(triage_system_prompt_template, {
    "full_name": profile["full_name"],
    "name":profile["name"],
    "examples": None,
    "user_profile_background": profile["user_profile_background"],
    "triage_no" : prompt_instructions["triage_rules"]["ignore"],
    "triage_notify": prompt_instructions["triage_rules"]["notify"],
    "triage_email" : prompt_instructions["triage_rules"]["respond"],
  }
)
user_prompt = create_prompt(triage_user_prompt_template, {
    "author": email["from"],
    "to": email["to"],
    "subject": email["subject"],
    "email_thread" : email["body"],
  }
)

triage_agent = Agent(
    name="Triage Agent",
    instructions=system_prompt,
    output_type=Router
)
     
@function_tool
def write_email(to: str, subject: str, content: str) -> str:
    """Write and send an email."""
    # Placeholder response - in real app would send email
    return f"Email sent to {to} with subject '{subject}'"
     
@function_tool
def schedule_meeting(
    attendees: list[str],
    subject: str,
    duration_minutes: int,
    preferred_day: str
) -> str:
    """Schedule a calendar meeting."""
    # Placeholder response - in real app would check calendar and schedule
    return f"Meeting '{subject}' scheduled for {preferred_day} with {len(attendees)} attendees"
   
@function_tool
def check_calendar_availability(day: str) -> str:
    """Check calendar availability for a given day."""
    # Placeholder response - in real app would check actual calendar
    return f"Available times on {day}: 9:00 AM, 2:00 PM, 4:00 PM"


store = InMemoryStore(
      index={
          "dims": 768,
          "embed": GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
      }
    )
@asynccontextmanager
async def get_store():
  yield store

class UserInfo(BaseModel):
  username: str

namespace_template=("email_assistant", "{username}", "collection")

# Initialize the manage memory tool dynamically:
manage_adapter = LangMemOpenAIAgentToolAdapter(
    lambda store, namespace=None: create_manage_memory_tool(namespace=namespace, store=store),
    store_provider=get_store,
    namespace_template=namespace_template
)
manage_memory_tool = manage_adapter.as_tool()

# Initialize the search memory tool dynamically:
search_adapter = LangMemOpenAIAgentToolAdapter(
    lambda store, namespace=None: create_search_memory_tool(namespace=namespace, store=store),
    store_provider=get_store,
    namespace_template=namespace_template
)
search_memory_tool = search_adapter.as_tool()

response_prompt_template = """
< Role >
You are {full_name}'s executive assistant. You are a top-notch executive assistant who cares about {name} performing as well as possible.
 Role >

< Tools >
You have access to the following tools to help manage {name}'s communications and schedule:

1. write_email(to, subject, content) - Send emails to specified recipients
2. schedule_meeting(attendees, subject, duration_minutes, preferred_day) - Schedule calendar meetings
3. check_calendar_availability(day) - Check available time slots for a given day
 Tools >

< Instructions >
{instructions}
 Instructions >
"""

response_system_prompt = create_prompt(response_prompt_template, {
    "full_name": profile["full_name"],
    "name":profile["name"],
    "instructions": prompt_instructions["agent_instructions"] + "Always save my email interactions in memory store for later discussions.",
  }
)

tools=[write_email, schedule_meeting, check_calendar_availability, manage_memory_tool, search_memory_tool]
# async def run_triage_agent():
#     triage_result = await Runner.run(triage_agent, user_prompt, run_config = config)
#     print(triage_result.final_output.classification)
#     print(triage_result.final_output.reasoning)
    
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(run_triage_agent())


response_agent = Agent[UserInfo](
    name="Response agent",
    instructions=response_system_prompt,
    tools=tools
    )
async def triage_router(email: Email, username: str):

  user_prompt = create_prompt(triage_user_prompt_template, {
    "author": email.from_,
    "to": email.to,
    "subject": email.subject,
    "email_thread" : email.body,
  })

  # print(user_prompt)

  triage_result = await Runner.run(
      triage_agent,
      user_prompt,
      run_config = config,
      context=UserInfo(username=username)
      )
  print(triage_result.final_output)
  print("Triage History: ", triage_result.to_input_list())
  async with get_store() as store:
        namespace=("email_assistant", "Junaid", "collection")
        res = await store.asearch(namespace)
        for i, mem in enumerate(res):
            print(i,": ", mem.value['content'])
  if triage_result.final_output.classification == "respond":
        print("📧 Classification: RESPOND - This email requires a response")
        response_result = await Runner.run(
            response_agent,
            f"Respond to the email {email.model_dump_json(by_alias=True)}",
            run_config = config,
            context=UserInfo(username=username)
            )
        print(response_result.final_output)
        print("Response History", response_result.to_input_list())
  elif triage_result.final_output.classification == "ignore":
      print("🚫 Classification: IGNORE - This email can be safely ignored")
  elif triage_result.final_output.classification == "notify":
      # If real life, this would do something else
      print("🔔 Classification: NOTIFY - This email contains important information")
  else:
      raise ValueError(f"Invalid classification: {triage_result.final_output.classification}")
  
if __name__ == "__main__":
    import asyncio
    username = "ahmed"
    asyncio.run(triage_router(email_model, username))
    
    