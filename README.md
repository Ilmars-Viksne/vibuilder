# Vibuilder: Autonomous Coding Agent

Vibuilder is a lightweight, provider-agnostic autonomous coding agent that works with NVIDIA NIM, OpenRouter, Ollama, LM Studio, and other OpenAI-compatible endpoints.

## Features

- **Provider Agnostic:** Easily switch between different LLM providers using a Registry pattern.
- **Autonomous Workflow:** Follows a structured Plan -> Design -> Execute -> Verify loop.
- **Isolated Workspace:** All agent operations are confined to a `agent_workspace/` directory.
- **Persistent Memory:** Action history is saved to JSON for auditing and resumption.
- **Integrated Tools:** Built-in support for Python execution, Pytest, and Git.

## Prerequisites

- Python 3.10+
- API keys for NIM or OpenRouter (optional)
- Local LLM setup with Ollama or LM Studio (optional)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd vibuilder
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Configuration

Edit `config/config.yaml` to set your preferred provider and models:

```yaml
provider: nim

providers:
  nim:
    model: meta/llama-3.3-70b-instruct
    api_key_env: NIM_API_KEY
  openrouter:
    model: anthropic/claude-3.5-sonnet
    api_key_env: OPENROUTER_API_KEY
  ollama:
    model: qwen2.5-coder:32b
  lmstudio:
    model: local-model
  mock:
    model: mock-model
```

## Usage

Run the agent via the CLI:

```bash
python main.py --goal "Build a FastAPI ToDo API with SQLite" --provider openrouter
```

### Options

- `--goal`: The task for the agent to complete (required).
- `--provider`: Override the default provider from `config.yaml`.
- `--max-steps`: Maximum autonomous execution steps (default: 50).

## Running Tests

Run the full test suite with:

```bash
PYTHONPATH=. pytest -q
```

You can also run a syntax/import check with:

```bash
python -m compileall .
```

## Architecture

1.  **Planner:** Breaks down the goal into a list of actionable steps.
2.  **Architect:** Designs the system structure and file organization.
3.  **Coder:** Executes the plan by generating code and performing file operations.
4.  **Executor:** Runs the tools (Filesystem, Python, Pytest, Git) and returns feedback.
5.  **Tester:** Evaluates test results and suggests fixes.
6.  **Reviewer:** Provides a final assessment of the completed work.

### Agent Action Schema

The coder must return one JSON object per step. Supported actions are:

```json
{"action": "create_folder", "path": "path/to/dir"}
{"action": "create_file", "path": "path/to/file", "content": "file content"}
{"action": "edit_file", "path": "path/to/file", "content": "new content"}
{"action": "replace_text", "path": "path/to/file", "search": "old text", "replace": "new text"}
{"action": "run_python", "path": "path/to/script.py"}
{"action": "run_tests"}
{"action": "git_init"}
{"action": "git_commit", "message": "commit message"}
{"action": "finish"}
```

All file paths must be relative to `agent_workspace/`. Absolute paths and path traversal are rejected.

### Workspace Safety Model

Vibuilder performs all filesystem operations inside `agent_workspace/`.

The action validator rejects obvious unsafe paths such as absolute paths and `..` traversal. The workspace manager also resolves every path against the workspace root and rejects paths that escape the workspace.

## Testing with Mock Provider

You can test the framework without an API key using the `mock` provider:

```bash
python main.py --goal "Create a hello script" --provider mock --max-steps 5
```
