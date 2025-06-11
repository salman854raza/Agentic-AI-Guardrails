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


