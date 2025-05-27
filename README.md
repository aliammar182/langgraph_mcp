
# 🚀 MCP PR Analyzer

A modern, tool-augmented AI agent for **automated GitHub Pull Request (PR) analysis** and reporting to Notion, powered by [OpenAI](https://platform.openai.com/), [LangGraph](https://github.com/langchain-ai/langgraph), [MCP](https://github.com/langchain-ai/mcp), and the [Notion SDK](https://github.com/ramnes/notion-sdk-py).  
Python environment management is fast and reproducible via [`uv`](https://github.com/astral-sh/uv).

---

## ✨ Features

- **Automated PR Analysis**: Review and summarize GitHub PRs using GPT-4 and LangGraph.
- **MCP Server**: Tool-based architecture for extensible agent abilities.
- **Notion Integration**: Write PR insights directly to your Notion workspace.
- **Modern Python Management**: Uses `uv` for speedy, consistent environments.
- **Interactive CLI**: Start, analyze, and save PR reports from your terminal.

---

## 🗂️ Project Structure

```
.
├── agent.py              # Main CLI entrypoint and agent runner
├── pr_analyzer.py        # MCP server: PR and Notion tools
├── github_integration.py # GitHub API utilities
├── requirements.txt      # All Python dependencies
├── .env.example          # Example .env file with required keys
└── README.md             # This file
```

---

## ⚡ Quickstart

### 1. Install [uv](https://github.com/astral-sh/uv)

```bash
pip install uv
```

### 2. Clone this repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your API keys:

```env
GITHUB_TOKEN=your_github_token
NOTION_API_KEY=your_notion_secret
NOTION_PAGE_ID=your_notion_page_id
OPENAI_API_KEY=your_openai_key
```

**Environment Variable Details:**
- `GITHUB_TOKEN`: [GitHub personal access token](https://github.com/settings/tokens) with `repo` scope.
- `NOTION_API_KEY`: [Notion integration token](https://www.notion.so/my-integrations) (secret_xxx...).
- `NOTION_PAGE_ID`: ID of your Notion page or database (copy from Notion URL).
- `OPENAI_API_KEY`: [OpenAI API key](https://platform.openai.com/api-keys).

---

## 🚦 Usage

Start the agent with:

```bash
python agent.py
```

You'll be prompted:

```
❓ What would you like the agent to do?
```

Paste a PR URL or describe your task. The agent will analyze the PR and offer to save the results to Notion.

---

## 🛠️ How It Works

- **agent.py**  
  Runs the interactive agent, powered by OpenAI + LangGraph, with tool-calling via MCP.
- **pr_analyzer.py**  
  Exposes tools to:
    - Fetch PR data from GitHub
    - Save analysis to Notion
- **github_integration.py**  
  Handles GitHub API authentication and data retrieval.

---

## 🧩 Extending

- **Add new tools:** Edit `pr_analyzer.py` to provide more agent abilities.
- **Change models:** Set a different model in `agent.py`.
- **Customize Notion output:** Adjust Notion templates in the Notion tool.

---

## 🤝 Contributing

PRs and issues are welcome!  
Please open an issue for bugs or feature requests.

---

## 📜 License

MIT

---

## 🌟 Credits

- [OpenAI](https://platform.openai.com/)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [MCP](https://github.com/langchain-ai/mcp)
- [Notion SDK for Python](https://github.com/ramnes/notion-sdk-py)
- [uv](https://github.com/astral-sh/uv)
