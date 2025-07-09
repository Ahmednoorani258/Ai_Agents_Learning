from tools import check_calendar_availability, schedule_meeting, write_email,manage_memory_tool,search_memory_tool
from models import UserInfo, Email, Router, email_model
from prompts import system_prompt,triage_user_prompt_template,response_system_prompt
from memory import get_store
from helper_function import create_prompt
from agents import (
    Agent,
    Runner,
)
from setupconfig import config
import asyncio


triage_agent = Agent(
    name="Triage Agent",
    instructions=system_prompt,
    output_type=Router
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
    
    