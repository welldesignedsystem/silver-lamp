from mcp.server.fastmcp import FastMCP
from starlette.responses import PlainTextResponse

mcp = FastMCP(
    name="RunningServerBasic",
    instructions="This is a basic example of a running MCP server.",
    host="127.0.0.1",
    port=8081
)

@mcp.resource(uri="quote://{name}/say-hi", name="hi", description="say hi to the user.")
async def say_hi(name) -> str:
    """
    Say hi to the user.

    Args:
        name: The name of the user to greet, along with the hand emoji.
    """
    return f"Hello, {name}! 👋"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")


