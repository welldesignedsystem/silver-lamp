from fastmcp.dependencies import Depends
from fastmcp import FastMCP
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

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request) -> PlainTextResponse:
    return PlainTextResponse("OK", status_code=200)

def get_user_id() -> str:
    return "user_123"  # Injected at runtime

@mcp.tool
def get_user_details(user_id: str = Depends(get_user_id)) -> str:
    # user_id is injected by the server, not provided by the LLM
    return f"Details for {user_id}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")


