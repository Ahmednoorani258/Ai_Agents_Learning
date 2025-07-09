from memory import manager, store
from setupconfig import config
from tools import (
    write_email,
    schedule_meeting,
    check_calendar_availability,
    manage_memory_tool,
    search_memory_tool,
)
from agents import Agent, Runner
from prompts import response_system_prompt, triage_system_prompt_template, triage_user_prompt_template, prompt_instructions, profile
from models import UserInfo, Email, Router

from helper_function import create_prompt,format_few_shot_examples


tools=[write_email, schedule_meeting, check_calendar_availability, manage_memory_tool, search_memory_tool]
response_agent = Agent[UserInfo](
    name="Response agent",
    instructions=response_system_prompt,
    tools=tools
    )
conversation = [
    {
        "role": "user",
        "content": "What's a binary tree? I work with family trees if that helps",
    },
    {
        "role": "assistant",
        "content": "A binary tree is like a family tree, but each parent has at most 2 children. Here's a simple example:\n   Bob\n  /  \\nAmy  Carl\n\nJust like in family trees, we call Bob the 'parent' and Amy and Carl the 'children'.",
    },
    {
        "role": "user",
        "content": "Oh that makes sense! So in a binary search tree, would it be like organizing a family by age?",
    },
]

episodes = manager.invoke({"messages": conversation})


async def triage_router(email: Email, username: str):

    namespace = (
        "email_assistant",
        username,
        "examples"
    )

    examples = store.search(
        namespace,
        query=str({"email": email.model_dump()}),
    )
    examples=format_few_shot_examples(examples)

    system_prompt = create_prompt(triage_system_prompt_template, {
        "full_name": profile["full_name"],
        "name":profile["name"],
        "user_profile_background": profile["user_profile_background"],
        "triage_no" : prompt_instructions["triage_rules"]["ignore"],
        "triage_notify": prompt_instructions["triage_rules"]["notify"],
        "triage_email" : prompt_instructions["triage_rules"]["respond"],
        "examples": examples,
      }
    )

    user_prompt = create_prompt(triage_user_prompt_template, {
      "author": email.from_,
      "to": email.to,
      "subject": email.subject,
      "email_thread" : email.body
    })

    triage_agent = Agent(
        name="Triage Agent",
        instructions=system_prompt,
        output_type=Router
    )

    triage_result = await Runner.run(
        triage_agent,
        user_prompt,
        run_config = config,
        context=UserInfo(username=username)
        )

    print(triage_result.final_output)
    print("Triage History: ", triage_result.to_input_list())

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
    
    return
async def main():
        
    email_input = {
        "from": "Tom Jones ",
        "to": "Muhammad Junaid Shaukat ",
        "subject": "Purchase API documentation",
        "body": """Hi John - I want to buy documentation?""",
    }

    typed_email = Email(**email_input)
    username = "Junaid"
    await triage_router(typed_email, username)
    
    email_input2 = {
    "from": "Alice Smith ",
    "to": "Muhammad Junaid Shaukat ",
    "subject": "Urgent Help for API documentation",
    "body": """Hi Junaid,

    I was reviewing the API documentation for the new authentication service and noticed a few endpoints seem to be missing from the specs. Could you help clarify if this was intentional or if we should update the docs?

    Specifically, I'm looking at:
    - /auth/refresh
    - /auth/validate

    Thanks!
    Alice""",
    }

    typed_email2 = Email(**email_input2)
    username = "Junaid"
    await triage_router(typed_email2, username)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    
    namespace=("email_assistant", "Junaid", "collection")
    res = store.search(namespace)
    print(res)