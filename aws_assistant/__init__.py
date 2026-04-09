from mcp.server.fastmcp import FastMCP

mcp = FastMCP("aws-assistant")

# Import tools so they register with the mcp instance
import aws_assistant.tools.deployment  # noqa: E402, F401
import aws_assistant.tools.component   # noqa: E402, F401
