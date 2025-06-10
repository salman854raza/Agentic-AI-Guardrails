# AI Guardrail System Imports Explained
#for more information of code. I provided here the link of Google Colab code:-
# https://colab.research.google.com/drive/1Zc5BmH-boObiiIJpjEXO5lLti3hkv8si?usp=sharing

# Guardrails in OpenAI Agents SDK

## Summary
OpenAI has included guardrails in the Agents SDK, which come in two types:
- **Input Guardrails**: Check that the input to your LLM is "safe"
- **Output Guardrails**: Check that the output from your LLM is "safe"

Guardrails run in parallel to your agents, enabling checks and validations of user input. 

**Example Use Case**:  
If you have an agent using a slow/expensive model for customer requests, you wouldn't want users asking for math homework help. A guardrail with a fast/cheap model can detect this and raise an error before the expensive model runs, saving time and money.

## Types of Guardrails
1. **Input Guardrails**: Run on the initial user input
2. **Output Guardrails**: Run on the final agent output

[Reference Documentation](https://openai.github.io/openai-agents-python/guardrails/)

## Input Guardrails
### Execution Flow
1. Receives the same input passed to the agent
2. Guardrail function runs, producing a `GuardrailFunctionOutput` (wrapped in `InputGuardrailResult`)
3. Checks if `.tripwire_triggered` is true:
   - If true: Raises `InputGuardrailTripwireTriggered` exception
   - Allows appropriate user response or exception handling

### Implementation Notes
- Run only on user input (only for the first agent in a chain)
- Guardrails are defined on the Agent rather than passed to `Runner.run` because:
  - Different agents typically need different guardrails
  - Colocating guardrails with agents improves code readability

## Tripwires
- When input/output fails a guardrail check:
  - Guardrail signals this with a tripwire
  - System immediately raises either:
    - `InputGuardrailTripwireTriggered` or
    - `OutputGuardrailTripwireTriggered`
  - Agent execution halts immediately
## 1. `import asyncio`
**Purpose**: Enables asynchronous programming  
**Why Needed**:
- Allows multiple guardrails to run concurrently
- Prevents blocking during AI processing
- Essential for handling multiple simultaneous requests  
**Used For**:
- `async/await` functions
- Running guardrails in parallel
- Efficient I/O operations with AI models

## 2. `from pydantic import BaseModel`
**Purpose**: Data validation and settings management  
**Why Needed**:
- Ensures all inputs/outputs follow defined formats
- Automatic data type validation
- Clean serialization/deserialization  
**Used For**:
- Defining `Message` and `MathCheck` models
- Validating agent inputs/outputs
- Structured error messages

## 3. `from agents import (...)`
### Core Framework Components

### a) `Agent`
**Purpose**: Blueprint for AI agents  
**What It Does**:
- Contains agent name, instructions, capabilities
- Tracks input/output guardrails
- Defines expected output format  
**Example Use**:
```python
homework_agent = Agent(name="Helper", instructions="Help with homework")