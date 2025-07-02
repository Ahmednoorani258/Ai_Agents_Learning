from pydantic import BaseModel
from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, Runner, TResponseInputItem,output_guardrail , input_guardrail
from setupconfig import config

class MessageOutput(BaseModel):
    response: str

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)

guardrail_agent2 = Agent(
    name="Guardrail check",
    instructions="Check if the output includes any math.",
    output_type=MathHomeworkOutput,
)
@input_guardrail
async def math_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context, run_config = config)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )

@output_guardrail
async def math_output_guardrail(
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    print(f"Output: Guardrail triggered", output)
    result = await Runner.run(guardrail_agent2, output, context=ctx.context, run_config = config)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )

agent: Agent = Agent(
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[math_guardrail],
    output_guardrails=[math_output_guardrail]
)

def main():
    try:
        # Run the agent with a sample input
        result = Runner.run_sync(
            starting_agent=agent,
            input="hi, can you solve this math problem for me? What is 2 + 2?",
            context=None,  # No specific context needed for this example
            run_config=config
        )
        
        print(f"Final Output: {result.final_output.response}")
        print(f"Tripwire Triggered: {result.final_output.is_math_homework}")
    except Exception as e:
        print("Guardrail triggered! The input violates the guardrail conditions.")
        print(f"Details: {e}")
    
if __name__ == "__main__":

    main()