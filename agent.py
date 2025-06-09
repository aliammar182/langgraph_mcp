import asyncio
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from pprint import pprint
from supabase import create_client
from dotenv import load_dotenv
from openai import OpenAI
from memory.memory_tools import save_memory, search_memories, invoke_search_memories
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Initialize OpenAI client for embeddings
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

model = ChatOpenAI(model="gpt-4.1-nano-2025-04-14")

server_params = StdioServerParameters(
    command="python",
    args=["pr_analyzer.py"],  # path to your math_server/pr_analyzer
)

def get_embedding(text):
    """Get embedding for the given text using OpenAI's text-embedding-3-small model."""
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {str(e)}")
        return None

def is_pr_question(question: str) -> bool:
    """Check if the question is about a PR."""
    pr_keywords = ['pr', 'pull request', 'github pr', 'merge request']
    return any(keyword in question.lower() for keyword in pr_keywords)

def extract_ai_response_and_analysis(messages):
    """Extract the final AI response and analysis from the messages."""
    ai_response = ""
    analysis = ""
    
    # First pass: find the last AI response
    for msg in reversed(messages):
        if msg.__class__.__name__ == "AIMessage":
            ai_response = msg.content
            break
    
    # Second pass: find the analysis from tool calls
    for msg in messages:
        if msg.__class__.__name__ == "AIMessage":
            if hasattr(msg, "additional_kwargs") and isinstance(msg.additional_kwargs, dict):
                tool_calls = msg.additional_kwargs.get("tool_calls", [])
                if tool_calls:
                    # Look for create_notion_page tool calls
                    for tool_call in tool_calls:
                        if tool_call.get('function', {}).get('name') == 'create_notion_page':
                            # Extract just the arguments from the tool call
                            arguments = tool_call.get('function', {}).get('arguments', '')
                            try:
                                # Parse the arguments JSON to get the content
                                args_dict = json.loads(arguments)
                                analysis = args_dict.get('content', '')
                            except json.JSONDecodeError:
                                analysis = arguments
                            return ai_response, analysis
    
    return ai_response, analysis

async def process_message(user_message: str, agent, session) -> None:
    """Process a single user message."""
    # First, search for relevant memories
    print("\n🔍 Searching for relevant memories...")
    relevant_memories = invoke_search_memories(user_message)
    
    # Prepare memory context
    memory_context = ""
    if relevant_memories and relevant_memories[0] != "No similar memories found":
        print("\n📚 Found relevant memories:")
        for memory in relevant_memories:
            print(memory)
            memory_context += f"\n{memory}"
    else:
        print("\n📚 No relevant memories found")

    # Create system message with memory context
    system_message = SystemMessage(content=f"""You are a helpful AI assistant. Use the following relevant memories to help answer the user's question:
    {memory_context}
    
    If the memories contain relevant information, use it in your response. If not, say you don't have that information.""")
    
    # Send the user's message to the agent with memory context
    print("\n🤖 Processing your request...")
    response = await agent.ainvoke({
        "messages": [
            system_message,
            HumanMessage(content=user_message)
        ]
    })
    messages = response["messages"]
    
    # Extract the final AI response and analysis
    ai_response, analysis = extract_ai_response_and_analysis(messages)
    
    # Save to conversations table and create embedding
    try:
        # First save to conversations table
        conversation_response = supabase.table('conversations').insert({
            'user_question': user_message,
            'chatbot_answer': ai_response,
            'analysis': analysis if is_pr_question(user_message) else ""
        }).execute()
        
        # Get the conversation ID
        conv_id = conversation_response.data[0]['id']
        
        # For PR questions, save question and analysis
        # For other questions, save question and answer separately
        if is_pr_question(user_message):
            combined_text = f"Question: {user_message}\nAnalysis: {analysis}"
        else:
            combined_text = f"Question: {user_message}\nAnswer: {ai_response}"
        
        # Save as memory with conversation ID
        memory_result = save_memory.invoke({"memory": combined_text, "conv_id": conv_id})
        print(f"\n💾 Memory saved: {memory_result}")
            
    except Exception as e:
        print(f"\n❌ Error saving to database: {str(e)}")

    print("\n🤖 Agent response:\n")
    for msg in messages:
        # 1) Figure out what kind of message it is:
        msg_type = msg.__class__.__name__           # "HumanMessage", "AIMessage", or "ToolMessage"
        print(f"--- {msg_type} ---")

        # 2) Print the one field you almost always want first: .content
        print("Content:")
        print(msg.content)
        print()

        # 3) If it's an AIMessage, it might have tool_calls in additional_kwargs
        if hasattr(msg, "additional_kwargs") and isinstance(msg.additional_kwargs, dict):
            tc = msg.additional_kwargs.get("tool_calls")
            if tc:
                print(" Tool calls:")
                pprint(tc, indent=2)

        # 4) If it's a ToolMessage, you might want to see .name (function name) or .content (usually JSON)
        if msg_type == "ToolMessage":
            print(" Function name: ", getattr(msg, "name", "(no name)"))
            print(" Raw tool output:")
            print(msg.content)
        print("\n")

async def run_agent_interactive():
    """Run the agent in an interactive loop."""
    print("\n🤖 Starting interactive session. Type 'exit' to quit.")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Load MCP tools
            mcp_tools = await load_mcp_tools(session)
            # Combine MCP tools with memory tools
            all_tools = mcp_tools + [save_memory, search_memories]
            agent = create_react_agent(model, all_tools)
            
            while True:
                # Ask the user for their question
                loop = asyncio.get_event_loop()
                user_message = await loop.run_in_executor(None, lambda: input("\n❓ What would you like the agent to do? "))
                
                # Check if user wants to exit
                if user_message.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Goodbye!")
                    break
                
                # Process the message
                await process_message(user_message, agent, session)

if __name__ == "__main__":
    asyncio.run(run_agent_interactive())
