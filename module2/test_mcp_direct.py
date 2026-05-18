import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_calendar_mcp():
    """Connect directly to the Google Calendar MCP server"""
    
    print("Connecting to MCP server...\n")
    
    # Server parameters - point to the MCP server you just authorized
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@a-bonus/google-docs-mcp"],
        env=None
    )
    
    # Connect to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            print("✅ Connected to MCP server\n")
            
            # List available tools
            tools_result = await session.list_tools()
            
            print("📋 Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n" + "="*60)
            
            # Call the calendar tool
            print("\n📅 Fetching today's calendar events...\n")
            
            # Find the calendar list tool
            calendar_tool = None
            for tool in tools_result.tools:
                if "calendar" in tool.name.lower() and "list" in tool.name.lower():
                    calendar_tool = tool.name
                    break
            
            if calendar_tool:
                result = await session.call_tool(
                    calendar_tool,
                    arguments={}
                )
                
                print(f"Result from {calendar_tool}:")
                print(json.dumps(result.content, indent=2))
            else:
                print("⚠️  No calendar list tool found. Available tools:")
                for tool in tools_result.tools:
                    print(f"  - {tool.name}")

if __name__ == "__main__":
    asyncio.run(test_calendar_mcp())