from mcp.server.fastmcp import FastMCP
from starlette.responses import PlainTextResponse

mcp = FastMCP(
    name="RunningServerBasic",
    instructions="This is a basic example of a running MCP server.",
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

app = mcp.streamable_http_app()

############################################################################
# uvicorn 02:app --host 0.0.0.0 --port 8081                                #
# INFO:     Started server process [99162]                                 #
# INFO:     Waiting for application startup.                               #
# [02/08/26 14:47:16] INFO     StreamableHTTP session manager started      #                                                                                                                             streamable_http_manager.py:116
# INFO:     Application startup complete.                                  #
# INFO:     Uvicorn running on http://0.0.0.0:8081 (Press CTRL+C to quit)  #
############################################################################

