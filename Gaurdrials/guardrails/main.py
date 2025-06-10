from pydantic import BaseModel
import asyncio

# Data models
class Message(BaseModel):
    response: str

class MathCheck(BaseModel):
    is_math: bool
    reasoning: str

# Simulated Agent Framework
class Agent:
    def __init__(self, name: str, instructions: str, output_type=None):
        self.name = name
        self.instructions = instructions
        self.output_type = output_type

class Runner:
    @staticmethod
    async def run(agent, input_text):
        # Simulate processing
        return type('Response', (), {
            'final_output': agent.output_type(response=f"Processed: {input_text}") 
            if agent.output_type else f"Processed: {input_text}"
        })

# Input Guardrail
async def input_math_check(ctx, agent, input_text):
    math_keywords = ['solve', 'calculate', '=', 'x +']
    is_math = any(kw in input_text.lower() for kw in math_keywords)
    
    return type('Output', (), {
        'output_info': MathCheck(is_math=is_math, reasoning="Keyword detection"),
        'tripwire_triggered': is_math
    })

# Main Agent
homework_agent = Agent(
    name="Homework Helper",
    instructions="Help students but don't solve math",
    output_type=Message
)

# Test function
async def test_guardrails():
    tests = [
        ("What's the capital of France?", False),
        ("Solve 2x + 5 = 15", True),
    ]
    
    for text, should_block in tests:
        print(f"\nInput: '{text}'")
        result = await input_math_check(None, None, text)
        if result.tripwire_triggered:
            print(f"🚫 BLOCKED (Math detected: {result.output_info.reasoning})")
        else:
            response = await Runner.run(homework_agent, text)
            print(f"✅ ALLOWED: {response.final_output.response}")

if __name__ == "__main__":
    print("=== Math Homework Guardrail Demo ===")
    asyncio.run(test_guardrails())
# EOF

# 5. Run the demo
# python guardrails.py