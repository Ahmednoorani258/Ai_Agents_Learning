from helper_function import create_prompt



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