#Output Guardrais
from pydantic import BaseModel
from agents import Agent, Runner, output_guardrail, GuardrailFunctionOutput, OutputGuardrailTripwireTriggered

class Message(BaseModel):
    response: str

class MathDetected(BaseModel):
    reasoning: str
    is_math: bool #true

check_agent = Agent(
    name="Homework Check",
    instruction="check karo ke kya output me math solution hai?",
    output_type=MathDetected,
)

@output_guardrail
async def output_check(ctx, agent, output: Message):
    result = await Runner.run(check_agent, output.response, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math
    )
agent = Agent(
    name="Support Agent",
    instructions="customer support does not solve math problem",
    output_type=Message,
)

async def main():
    try:
        await Runner.run(agent, "please solved: 2x+3 = 11?")
    except:
        print("output guardrails triggered: math solution blocked successfully.")