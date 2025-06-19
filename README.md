# LangGraph MCP Agent with Memory

An intelligent agent built with LangGraph and MCP that can analyze pull requests and maintain a semantic memory of conversations using Supabase vector similarity search.

## Features

- 🤖 Interactive agent that can analyze GitHub pull requests
- 🧠 Semantic memory system using Supabase vector similarity search
- 🔍 Retrieves up to 5 most relevant past conversations
- 💾 Automatically saves conversations and their embeddings
- 🔄 Continuous operation with memory context
- 📊 Different handling for PR and general questions

## Prerequisites

- Python 3.8+
- Supabase account with vector similarity enabled
- OpenAI API key
- GitHub access (for PR analysis)

## Installation

1. Clone the repository:
```bash
git clone <repo_url>
cd langgraph_mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

4. Set up Supabase:
   - Create a new Supabase project
   - Enable the `pgvector` extension
   - Run the SQL function in `memory/similarity_search.sql`
   - Create the required tables:
     ```sql
     CREATE TABLE conversations (
         id SERIAL PRIMARY KEY,
         user_question TEXT NOT NULL,
         chatbot_answer TEXT NOT NULL,
         analysis TEXT,
         created_at TIMESTAMPTZ DEFAULT NOW()
     );

     CREATE TABLE notion_embedding (
         id SERIAL PRIMARY KEY,
         conv_id INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
         ques_analysis TEXT NOT NULL,
         embedding VECTOR(1536),
         created_at TIMESTAMPTZ DEFAULT NOW()
     );
     ```

## Usage

Run the agent:
```bash
python agent.py
```

The agent will:
1. Start an interactive session
2. Search for relevant memories before each response
3. Process your questions and maintain context
4. Save conversations and their embeddings

Example interactions:
```
❓ What would you like the agent to do? what is pr 484 about?
[Agent analyzes PR and saves memory]

❓ What would you like the agent to do? what does katie likes?
[Agent uses memory to answer and saves new memory]

❓ What would you like the agent to do? exit
👋 Goodbye!
```

## Memory System

The agent uses a semantic memory system that:
- Converts questions and answers to embeddings using OpenAI's text-embedding-3-small
- Stores embeddings in Supabase with vector similarity search
- Retrieves up to 5 most relevant past conversations
- Uses a similarity threshold of 0.3 for memory retrieval
- Maintains different formats for PR and general questions

### Memory Enhancements

The memory system can be further enhanced by:

1. **Metadata Filtering**:
   - Add metadata columns to the `notion_embedding` table:
     ```sql
     ALTER TABLE notion_embedding
     ADD COLUMN category TEXT,
     ADD COLUMN tags TEXT[],
     ADD COLUMN importance INTEGER;
     ```
   - Use metadata to filter memories before similarity search
   - Improve search performance by reducing the search space
   - Example: Filter by category before computing similarity

2. **User-Specific Memories**:
   - Add user identification to the schema:
     ```sql
     ALTER TABLE conversations
     ADD COLUMN user_id TEXT;
     
     ALTER TABLE notion_embedding
     ADD COLUMN user_id TEXT;
     ```
   - Implement user-specific memory retrieval
   - Maintain separate memory contexts for different users
   - Improve relevance by considering user history

3. **Performance Optimizations**:
   - Create indexes on metadata columns
   - Use partial indexes for common filters
   - Implement caching for frequent queries
   - Example index:
     ```sql
     CREATE INDEX idx_notion_embedding_user_category 
     ON notion_embedding(user_id, category);
     ```

4. **Memory Organization**:
   - Group related memories using tags
   - Implement memory hierarchies
   - Use categories for better organization
   - Example query with metadata:
     ```sql
     SELECT * FROM notion_embedding
     WHERE user_id = 'user123'
     AND category = 'preferences'
     ORDER BY importance DESC
     LIMIT 5;
     ```

### Agent-Level Memory Filtering

The agent supports powerful filtering capabilities for both PR analysis and general conversations. Here are some examples:

1. **PR Analysis with Filters**:
   ```
   ❓ What would you like the agent to do? [category:pr][tags:security,performance] analyze pr 484
   ```
   This will focus on security and performance aspects of the PR.

2. **Notion Page Filtering**:
   ```
   ❓ What would you like the agent to do? [notion:team-docs] what was the last security review?
   ```
   This will search within team documentation in Notion.

3. **Combined PR and Notion Filters**:
   ```
   ❓ What would you like the agent to do? [category:pr][notion:reviews] show me similar PRs
   ```
   This will find similar PRs and their Notion reviews.

4. **User-Specific PR Analysis**:
   ```
   ❓ What would you like the agent to do? [user:alice][category:pr] what PRs did I review?
   ```
   This will show PRs reviewed by Alice.

5. **Importance-Based PR Search**:
   ```
   ❓ What would you like the agent to do? [importance:high][category:pr] show critical PRs
   ```
   This will prioritize important PRs.

The agent automatically:
- Parses these filter commands from the user input
- Applies the filters before semantic search
- Combines filtered results with semantic similarity
- Maintains context across filtered conversations

Example interaction with PR and Notion:
```
❓ What would you like the agent to do? [category:pr][notion:security-reviews] analyze pr 484

🔍 Searching relevant PR memories in security reviews...
📚 Found relevant memories:
Similarity: 0.892
Memory: Question: what is pr 484 about?
Analysis: Security update for authentication system

🤖 Processing your request...
Based on my memory, PR 484 implements security improvements to the authentication system...
```

You can combine any of these filters to create powerful, context-aware searches. The agent will automatically handle the filtering and provide relevant results.

These enhancements can significantly improve:
- Memory retrieval speed
- Search relevance
- User experience
- System scalability

## Project Structure

```
langgraph_mcp/
├── agent.py              # Main agent implementation
├── pr_analyzer.py        # PR analysis functionality
├── memory/
│   ├── memory_tools.py   # Memory system implementation
│   └── similarity_search.sql  # Supabase vector similarity function
├── requirements.txt      # Project dependencies
└── README.md            # This file
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LangGraph for the agent framework
- Supabase for vector similarity search
- OpenAI for embeddings and language models
