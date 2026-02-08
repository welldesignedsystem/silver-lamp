from enum import Enum
from mcp.server.fastmcp import FastMCP
from starlette.responses import PlainTextResponse

mcp = FastMCP(
    name="RunningServerBasic",
    instructions="This is a basic example of a running MCP server.",
    host="127.0.0.1",
    port=8081
)
class Mood(str, Enum):
    SILLY = "silly"
    OPTIMISTIC = "optimistic"
    CYNICAL = "cynical"
    SARCASTIC = "sarcastic"
    PHILOSOPHICAL = "philosophical"

quotes = {
    "silly": "I'm not superstitious, but I am a little stitious.",
    "optimistic": "I intend to live forever. So far, so good.",
    "cynical": "Before you marry a person, you should first make them use a computer with slow internet to see who they really are.",
    "sarcastic": "I'm writing a book. I've got the page numbers done.",
    "philosophical": "The difference between stupidity and genius is that genius has its limits."
}

@mcp.resource(uri="quote://{mood}/generate", name="Quote", description="Get a random inspirational quote.")
async def get_inspirational_quote(mood: Mood) -> str:
    """
    Get an inspirational quote based on mood.

    Args:
        mood: Must be one of: silly, optimistic, cynical, sarcastic, philosophical
    """
    return quotes[mood.value]

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request) -> PlainTextResponse:
    return PlainTextResponse("OK", status_code=200)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")


