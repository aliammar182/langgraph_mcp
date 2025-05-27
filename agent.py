import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1-nano-2025-04-14")

server_params = StdioServerParameters(
    command="python",
    args=["pr_analyzer.py"],  # path to your math_server/pr_analyzer
)

async def run_agent_interactive():
    # Ask the user for their question or PR URL
    loop = asyncio.get_event_loop()
    user_message = await loop.run_in_executor(None, lambda: input("❓ What would you like the agent to do? "))

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)

            # Send the user's message to the agent
            response = await agent.ainvoke({"messages": user_message})
            print("\n🤖 Agent response:\n")
            print(response)

if __name__ == "__main__":
    asyncio.run(run_agent_interactive())
