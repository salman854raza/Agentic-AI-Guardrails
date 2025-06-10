# Code mein kya ho rha hai?
# AI {guardrial agent}
# Us se pochte ho: "Ye input math homework to nhi?"
# Agar wo ye kehta hai "Haan", to agent ko rok dow.

from pydantic import BaseModel
from agents import Agent, Runner, input_guardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered

class MathCheck(BaseModel):
    is_math_homework: bool #true
    reasoning: str

check_agent = Agent(
    name="Homework Check",
    instruction="is user want to do math homework?",
    output_type=MathCheck,
)

@input_guardrail
async def input_check(ctx, agent, input):
    result = await Runner.run(check_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework
    )

agent = Agent(
    name="Suport Agent",
    instruction="help the customer in solving maths problem..!",
    input_guardrail=[input_check],
)

async def main():
    try:
        await Runner.run(agent, "can you solve 2x+3 = 11?")
    except InputGuardrailTripwireTriggered:
        print("Input Guardrails Triggered: Maths Homework Blocked Because Its a Support Agent")



