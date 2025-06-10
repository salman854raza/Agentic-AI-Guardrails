from pydantic import BaseModel
import asyncio

# Simulating the agents framework for demonstration
class Agent:
    def __init__(self, name: str, instructions: str, output_type: type = None, input_guardrails: list = None, output_guardrails: list = None):
        self.name = name
        self.instructions = instructions
        self.output_type = output_type
        self.input_guardrails = input_guardrails or []
        self.output_guardrails = output_guardrails or []

class Runner:
    @staticmethod
    async def run(agent: Agent, input_text: str, context: dict = None):
        context = context or {}
        
        # Run input guardrails first
        for guardrail in agent.input_guardrails:
            result = await guardrail(context, agent, input_text)
            if result.tripwire_triggered:
                raise InputGuardrailTripwireTriggered(result.output_info)
        
        # Simulate agent processing
        response = f"Processed by {agent.name}: {input_text}"
        
        # Create output object
        output = agent.output_type(response=response) if agent.output_type else response
        
        # Run output guardrails
        for guardrail in agent.output_guardrails:
            result = await guardrail(context, agent, output)
            if result.tripwire_triggered:
                raise OutputGuardrailTripwireTriggered(result.output_info)
        
        return type('AgentResponse', (), {'final_output': output})

# Guardrail related classes
class GuardrailFunctionOutput:
    def __init__(self, output_info, tripwire_triggered: bool):
        self.output_info = output_info
        self.tripwire_triggered = tripwire_triggered

class InputGuardrailTripwireTriggered(Exception):
    pass

class OutputGuardrailTripwireTriggered(Exception):
    pass

def input_guardrail(func):
    return func

def output_guardrail(func):
    return func

# Our data models
class Message(BaseModel):
    response: str

class MathCheck(BaseModel):
    is_math: bool
    reasoning: str

# Input Guardrail Setup
check_input_agent = Agent(
    name="Input Math Detector",
    instructions="Does this input contain math homework problems? Answer true only if it's clearly a math problem to solve.",
    output_type=MathCheck
)

@input_guardrail
async def input_math_check(ctx, agent, input_text):
    # Simple detection - in real world you'd use a proper ML model
    math_keywords = ['solve', 'calculate', '=', 'x +', 'homework', 'math']
    is_math = any(keyword in input_text.lower() for keyword in math_keywords)
    
    result = await Runner.run(check_input_agent, input_text)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=is_math or result.final_output.is_math
    )

# Output Guardrail Setup
check_output_agent = Agent(
    name="Output Math Detector",
    instructions="Does this output contain math solutions?",
    output_type=MathCheck
)

@output_guardrail
async def output_math_check(ctx, agent, output: Message):
    # Simple detection
    math_indicator = '=' in output.response and ('x' in output.response or '+' in output.response)
    
    result = await Runner.run(check_output_agent, output.response)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=math_indicator or result.final_output.is_math
    )

# Main Agent
homework_agent = Agent(
    name="Homework Helper",
    instructions="Help students with their homework, but never solve math problems directly.",
    output_type=Message,
    input_guardrails=[input_math_check],
    output_guardrails=[output_math_check]
)

# Test cases
async def test_guardrails():
    test_cases = [
        ("What's the capital of France?", False),  # Should pass
        ("Solve for x: 2x + 5 = 15", True),      # Should be blocked by input guardrail
        ("Explain photosynthesis", False),        # Should pass
        ("Tell me about the equation E=mc^2", False),  # Should pass (discussion, not solving)
    ]
    
    for input_text, should_block in test_cases:
        print(f"\nTesting input: '{input_text}'")
        try:
            response = await Runner.run(homework_agent, input_text)
            print(f"SUCCESS: {response.final_output.response}")
            if should_block:
                print("ERROR: This should have been blocked!")
        except InputGuardrailTripwireTriggered:
            print("BLOCKED BY INPUT GUARDRAIL: Math homework detected in input")
            if not should_block:
                print("ERROR: This should have passed!")
        except OutputGuardrailTripwireTriggered:
            print("BLOCKED BY OUTPUT GUARDRAIL: Math solution detected in output")
            if not should_block:
                print("ERROR: This should have passed!")
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {str(e)}")

# Run the tests
if __name__ == "__main__":
    print("=== Testing Input and Output Guardrails ===")
    asyncio.run(test_guardrails())