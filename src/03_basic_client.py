import asyncio
from fastmcp import Client

client = Client("http://localhost:8081/mcp")

async def call_tool(name: str):
    async with client:
        print(await client.list_resource_templates())
        print(await client.read_resource("quote://Steve/say-hi"))

asyncio.run(call_tool("Ford"))