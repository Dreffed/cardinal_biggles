# quick_test.py
from langchain_ollama import ChatOllama

async def test():
    llm = ChatOllama(
        model="llama3.1",
        base_url="http://localhost:11434",
        temperature=0.1
    )

    response = await llm.ainvoke("Hello!")
    print(response.content)

import asyncio
asyncio.run(test())

