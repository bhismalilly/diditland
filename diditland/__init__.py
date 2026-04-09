from mcp.server.fastmcp import FastMCP

mcp = FastMCP("diditland")

# Import tools so they register with the mcp instance
import diditland.tools.deployment  # noqa: E402, F401
import diditland.tools.component   # noqa: E402, F401


def main():
    mcp.run(transport="stdio")
