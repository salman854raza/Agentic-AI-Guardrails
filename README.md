# Guardrails in OpenAI Agents SDK
# Guardrails
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
### Install openai-agents SDK
```
!pip install -Uq openai-agents pydantic
```
### Make your Notebook capable of running asynchronous functions.
The nest_asyncio library allows the existing event loop to accept nested event loops, enabling asyncio code to run within environments that already have an event loop, such as Jupyter notebooks.
In summary, both Jupyter notebooks and Python’s asyncio library utilize event loops to manage asynchronous operations. When working within Jupyter notebooks, it’s essential to be aware of the existing event loop to effectively run asyncio code without conflicts.
```
import nest_asyncio
nest_asyncio.apply()
```
```
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig
)
from google.colab import userdata
```
```
gemini_api_key = userdata.get("GEMINI_API_KEY")


# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")
```
```
#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)
```
## Implementation of Input Guardrail:
Checks that the input going into your LLM is "safe"
```
class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)


@input_guardrail
async def math_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context, run_config = config)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        # tripwire_triggered=False #result.final_output.is_math_homework,
        tripwire_triggered=result.final_output.is_math_homework,
    )
```
agent = Agent(
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[math_guardrail],
)
     
```
# This should trip the guardrail
try:
    result = await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?", run_config = config)
    print("Guardrail didn't trip - this is unexpected")
    print(result.final_output)

except InputGuardrailTripwireTriggered:
    print("Math homework guardrail tripped")
```
     
Math homework guardrail tripped
```
try:
    result = await Runner.run(agent, "Hello", run_config = config)
    print(result.final_output)

except InputGuardrailTripwireTriggered:
    print("Math homework guardrail tripped")
```
     
Hi there! How can I help you today?

### Implementation of Onput Guardrail:
The output guardrail checks that the output from your LLM is "safe".
```
class MessageOutput(BaseModel):
    response: str

class MathOutput(BaseModel):
    is_math: bool
    reasoning: str

guardrail_agent2 = Agent(
    name="Guardrail check",
    instructions="Check if the output includes any math.",
    output_type=MathOutput,
)

@output_guardrail
async def math_guardrail2(
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent2, output.response, context=ctx.context, run_config = config)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math,
    )
```
```
agent2 = Agent(
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    output_guardrails=[math_guardrail2],
    output_type=MessageOutput,
)
```
```     
# This should trip the guardrail
try:
    await Runner.run(agent2, "Hello, can you help me solve for x: 2x + 3 = 11?", run_config = config)
    print("Guardrail didn't trip - this is unexpected")

except OutputGuardrailTripwireTriggered:
    print("Math output guardrail tripped")
```
Math output guardrail tripped

### PIAIC Gaurdrails example
```
import asyncio
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrail,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
)

# Define the output model for the guardrail agent
class PIAICRelevanceOutput(BaseModel):
    is_piaic_relevant: bool
    reasoning: str

# Create the guardrail agent to check if input is PIAIC-related
guardrail_agent = Agent(
    name="PIAIC_Relevance_Check",
    instructions=(
        "You are a guardrail agent that checks if the user's input is related to PIAIC (Presidential Initiative for Artificial Intelligence and Computing) topics, "
        "such as Artificial Intelligence, Cloud Native Computing, Blockchain, Internet of Things (IoT), or other PIAIC courses. "
        "Determine if the input is relevant to PIAIC. "
        "Return a structured output with 'is_piaic_relevant' as a boolean and 'reasoning' explaining your decision."
    ),
    output_type=PIAICRelevanceOutput,
)

# Define the input guardrail function
async def piaic_relevance_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list,
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context, run_config = config)
    final_output = result.final_output_as(PIAICRelevanceOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_piaic_relevant,
    )

# Create the main PIAIC agent
piaic_agent = Agent(
    name="PIAIC_Assistant",
    instructions=(
        "You are a helpful assistant for PIAIC-related questions. "
        "Answer questions about PIAIC courses, such as AI, Cloud Native Computing, Blockchain, IoT, or other PIAIC initiatives. "
        "Provide accurate and concise information."
    ),
    input_guardrails=[InputGuardrail(guardrail_function=piaic_relevance_guardrail)],
)


try:
    result = await Runner.run(piaic_agent, "What is the curriculum for PIAIC's AI course?", run_config = config)
    print("Response:", result.final_output)
except InputGuardrailTripwireTriggered as e:
    print("Guardrail tripped: Input is not PIAIC-related.")
```
# Test with non-PIAIC input
``
try:
    result = await Runner.run(piaic_agent, "How do I bake a chocolate cake?", run_config = config)
    print("Response:", result.final_output)
except InputGuardrailTripwireTriggered as e:
    print("Guardrail tripped: Input is not PIAIC-related.")
```

Guardrail tripped: Input is not PIAIC-related.

# Input and Out Guardrails Example
```
import asyncio
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrail,
    InputGuardrailTripwireTriggered,
    OutputGuardrail,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
)

# Define the output model for the guardrail agents
class PIAICRelevanceOutput(BaseModel):
    is_piaic_relevant: bool
    reasoning: str

# Create the input guardrail agent to check if input is PIAIC-related
input_guardrail_agent = Agent(
    name="PIAIC_Input_Relevance_Check",
    instructions=(
        "You are a guardrail agent that checks if the user's input is related to PIAIC (Presidential Initiative for Artificial Intelligence and Computing) topics, "
        "such as Artificial Intelligence, Cloud Native Computing, Blockchain, Internet of Things (IoT), or other PIAIC courses. "
        "Determine if the input is relevant to PIAIC. "
        "Return a structured output with 'is_piaic_relevant' as a boolean and 'reasoning' explaining your decision."
    ),
    output_type=PIAICRelevanceOutput,
)

# Create the output guardrail agent to check if output is PIAIC-related
output_guardrail_agent = Agent(
    name="PIAIC_Output_Relevance_Check",
    instructions=(
        "You are a guardrail agent that checks if the agent's response is related to PIAIC (Presidential Initiative for Artificial Intelligence and Computing) topics, "
        "such as Artificial Intelligence, Cloud Native Computing, Blockchain, Internet of Things (IoT), or other PIAIC courses. "
        "Determine if the response content is relevant to PIAIC. "
        "Return a structured output with 'is_piaic_relevant' as a boolean and 'reasoning' explaining your decision."
    ),
    output_type=PIAICRelevanceOutput,
)

# Define the input guardrail function
async def piaic_input_relevance_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list,
) -> GuardrailFunctionOutput:
    result = await Runner.run(input_guardrail_agent, input, context=ctx.context, run_config = config)
    final_output = result.final_output_as(PIAICRelevanceOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_piaic_relevant,
    )

# Define the output guardrail function
async def piaic_output_relevance_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output: str | list,
) -> GuardrailFunctionOutput:
    result = await Runner.run(output_guardrail_agent, output, context=ctx.context, run_config = config)
    final_output = result.final_output_as(PIAICRelevanceOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_piaic_relevant,
    )

# Create the main PIAIC agent with both input and output guardrails
piaic_agent = Agent(
    name="PIAIC_Assistant",
    instructions=(
        "You are a helpful assistant for PIAIC-related questions. "
        "Answer questions about PIAIC courses, such as AI, Cloud Native Computing, Blockchain, IoT, or other PIAIC initiatives. "
        "Provide accurate and concise information."
    ),
    input_guardrails=[InputGuardrail(guardrail_function=piaic_input_relevance_guardrail)],
    output_guardrails=[OutputGuardrail(guardrail_function=piaic_output_relevance_guardrail)],
)


try:
    result = await Runner.run(piaic_agent, "What is the curriculum for PIAIC's AI course?", run_config = config)
    print("Response:", result.final_output)
except InputGuardrailTripwireTriggered as e:
    print("Input Guardrail tripped: Input is not PIAIC-related.")
except OutputGuardrailTripwireTriggered as e:
    print("Output Guardrail tripped: Response is not PIAIC-related.")
    ```

# Test with non-PIAIC input
```
try:
    result = await Runner.run(piaic_agent, "How do I bake a chocolate cake?", run_config = config)
    print("Response:", result.final_output)
except InputGuardrailTripwireTriggered as e:
    print("Input Guardrail tripped: Input is not PIAIC-related.")
except OutputGuardrailTripwireTriggered as e:
    print("Output Guardrail tripped: Response is not PIAIC-related.")
```
     
Input Guardrail tripped: Input is not PIAIC-related.

# Test with non-PIAIC input
```
try:
    result = await Runner.run(piaic_agent, "tell me about piaic founder, tell me about his current job title. he has left PIAIC as per my information. how he can cook chicken.", run_config = config)
    print("Response:", result.final_output)
except InputGuardrailTripwireTriggered as e:
    print("Input Guardrail tripped: Input is not PIAIC-related.")
except OutputGuardrailTripwireTriggered as e:
    print("Output Guardrail tripped: Response is not PIAIC-related.")
```
