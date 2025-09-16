from pipecat.services.openai.llm import OpenAILLMService
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
import asyncio
import os

async def main():
    llm = OpenAILLMService(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

    # Create a context with the message
    messages = [
        {
            "role": "user",
            "content": "Hello from Maya project!"
        }
    ]
    context = OpenAILLMContext(messages)

    # Run inference
    resp = await llm.run_inference(context)
    print(resp)

if __name__ == "__main__":
    asyncio.run(main())
