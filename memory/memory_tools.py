from typing import List, Optional, Dict, Any
from langchain.tools import tool
from supabase import create_client
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Initialize OpenAI client for embeddings
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str) -> Optional[List[float]]:
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

@tool
def save_memory(memory: str, conv_id: int) -> str:
    """Save memory to Supabase for later semantic retrieval.
    
    Args:
        memory: The memory text to save
        conv_id: The conversation ID to link this memory to
        
    Returns:
        str: Confirmation message
    """
    try:
        # Get embedding for the memory
        embedding = get_embedding(memory)
        if not embedding:
            return "Failed to generate embedding for memory"
            
        # Save to notion_embedding table
        response = supabase.table('notion_embedding').insert({
            'conv_id': conv_id,
            'ques_analysis': memory,
            'embedding': embedding
        }).execute()
        
        return f"Memory saved successfully with ID: {response.data[0]['id']}"
    except Exception as e:
        return f"Error saving memory: {str(e)}"

@tool
def search_memories(query: str, similarity_threshold: float = 0.3, match_count: int = 5) -> List[str]:
    """Search for the top-k most relevant memories using cosine similarity.
    
    Args:
        query: The search query
        similarity_threshold: Minimum similarity score (0-1)
        match_count: Number of top matches to return
        
    Returns:
        List[str]: List of relevant memories with their similarity scores
    """
    try:
        # Get embedding for the query
        query_embedding = get_embedding(query)
        if not query_embedding:
            return ["Failed to generate embedding for query"]
            
        # Call the Supabase function to find similar memories
        response = supabase.rpc(
            'find_similar_memories',
            {
                'query_embedding': query_embedding,
                'similarity_threshold': similarity_threshold,
                'match_count': match_count
            }
        ).execute()
        
        # Extract and return the memories with their similarity scores
        if not response.data:
            return ["No similar memories found"]
            
        memories = []
        for item in response.data:
            similarity = item['similarity']
            memory = item['ques_analysis']
            memories.append(f"Similarity: {similarity:.3f}\nMemory: {memory}\n")
            
        return memories
        
    except Exception as e:
        return [f"Error searching memories: {str(e)}"]

def invoke_search_memories(query: str) -> List[str]:
    """Helper function to invoke search_memories tool."""
    return search_memories.invoke({"query": query}) 