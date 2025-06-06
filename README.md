# MCP PR Reviewer with Supabase Integration

An AI-powered PR analysis tool that uses OpenAI's GPT-4 and embeddings to analyze pull requests using MCP (model context protocol) and store conversations in Supabase.

## Features

- Automated PR analysis using GPT-4
- Conversation storage in Supabase
- Semantic search capabilities using OpenAI embeddings
- Integration with Notion for documentation

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Supabase account and project
- OpenAI API key
- Docker (for local Supabase development)

## Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd <your-repo-name>
```

2. Create and activate a virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Create a `.env` file with your credentials:
```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Supabase Local Development Setup

1. Install the Supabase CLI:
```bash
npm install supabase --save-dev
```

2. Initialize Supabase in your project:
```bash
npx supabase init
```

3. Start the local Supabase stack:
```bash
npx supabase start
```

4. Access your local Supabase instance at http://localhost:54323

5. Get your local Supabase credentials:
```bash
npx supabase status
```

6. Update your `.env` file with local Supabase credentials:
```env
SUPABASE_URL=http://localhost:54323
SUPABASE_KEY=your_local_anon_key
```

## Database Setup

1. Create the conversations table:
```sql
CREATE TABLE conversations (
  id serial primary key,
  user_question text not null,
  chatbot_answer text not null,
  analysis text not null,
  timestamp timestamp default current_timestamp
);
```

2. Create the notion_embedding table:
```sql
CREATE TABLE notion_embedding (
    id            SERIAL         PRIMARY KEY,
    conv_id       INT            NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    ques_analysis TEXT           NOT NULL,
    embedding     VECTOR(1536),
    created_at    TIMESTAMPTZ    DEFAULT NOW()
);
```

## Usage

Run the agent:
```bash
python agent.py
```

The agent will:
1. Prompt for your question or PR URL
2. Analyze the PR using GPT-4
3. Save the conversation to Supabase
4. Generate and save embeddings for semantic search

## Development

This project uses:
- `uv` for package management
- `ruff` for linting
- `pyproject.toml` for project configuration

To run the linter:
```bash
ruff check .
```

## License

MIT
