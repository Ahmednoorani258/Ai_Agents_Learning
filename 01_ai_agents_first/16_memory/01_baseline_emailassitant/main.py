from agents import (
    Agent,
    Runner,
    function_tool
)
from typing import Dict
from setupconfig import config
from schemas import Email, Router
from prompts import (
    triage_system_prompt_template,
    triage_user_prompt_template,
    prompt_instructions,
)

email = {
    "from": "Alice Smith ",
    "to": "John Doe ",
    "subject": "Quick question about API documentation",
    "body": """
Hi John,

I was reviewing the API documentation for the new authentication service and noticed a few endpoints seem to be missing from the specs. Could you help clarify if this was intentional or if we should update the docs?

Specifically, I'm looking at:
- /auth/refresh
- /auth/validate

Thanks!
Alice""",
}


profile = {
    "name": "John",
    "full_name": "John Doe",
    "user_profile_background": "Senior software engineer leading a team of 5 developers",
}

# Example incoming email
email_model = Email(**email)
print(email_model.model_dump_json(by_alias=True))

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
    "instructions": prompt_instructions["agent_instructions"],
  }
)
print(response_system_prompt)


response_agent = Agent(
    name="Response agent",
    instructions=response_system_prompt,
    tools=[write_email, schedule_meeting, check_calendar_availability]
)


async def triage_router(email: Email):

  user_prompt = create_prompt(triage_user_prompt_template, {
    "author": email.from_,
    "to": email.to,
    "subject": email.subject,
    "email_thread" : email.body,
  })

  # print(user_prompt)

  triage_result = await Runner.run(triage_agent, user_prompt, run_config = config)
  print(triage_result.final_output)
  print("Triage History: ", triage_result.to_input_list())

  if triage_result.final_output.classification == "respond":
        print("📧 Classification: RESPOND - This email requires a response")
        response_result = await Runner.run(response_agent, f"Respond to the email {email.model_dump_json(by_alias=True)}", run_config = config)
        print(response_result.final_output)
        print("Response History", response_result.to_input_list())
  elif triage_result.final_output.classification == "ignore":
      print("🚫 Classification: IGNORE - This email can be safely ignored")
  elif triage_result.final_output.classification == "notify":
      # If real life, this would do something else
      print("🔔 Classification: NOTIFY - This email contains important information")
  else:
      raise ValueError(f"Invalid classification: {triage_result.final_output.classification}")


email_input = {
    "from": "Marketing Team ",
    "to": "John Doe ",
    "subject": "🔥 EXCLUSIVE OFFER: Limited Time Discount on Developer Tools! 🔥",
    "body": """Dear Valued Developer,

Don't miss out on this INCREDIBLE opportunity!

🚀 For a LIMITED TIME ONLY, get 80% OFF on our Premium Developer Suite!

✨ FEATURES:
- Revolutionary AI-powered code completion
- Cloud-based development environment
- 24/7 customer support
- And much more!

💰 Regular Price: 🎉
199/month!

🕒 Hurry! This offer expires in:
24 HOURS ONLY!

Click here to claim your discount: https://amazingdeals.com/special-offer

Best regards,
Marketing Team
---
To unsubscribe, click here
""",
}

typed_email = Email(**email_input)
print(typed_email.model_dump_json(by_alias=True))


email_input2 = {
    "from": "Alice Smith ",
    "to": "John Doe ",
    "subject": "Quick question about API documentation",
    "body": """Hi John,

I was reviewing the API documentation for the new authentication service and noticed a few endpoints seem to be missing from the specs. Could you help clarify if this was intentional or if we should update the docs?

Specifically, I'm looking at:
- /auth/refresh
- /auth/validate

Thanks!
Alice""",
}

typed_email2 = Email(**email_input2)
async def main():
    triage_result = await Runner.run(triage_agent, user_prompt, run_config = config)
    print(triage_result.final_output.classification)
    print(triage_result.final_output.reasoning)
    
    
    response_result = await Runner.run(response_agent, "what is my availability for tuesday?", run_config = config)
    print(response_result.final_output)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())