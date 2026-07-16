# Vibuilder: Autonomous Coding Agent

Vibuilder is a lightweight, provider-agnostic autonomous coding agent that works with NVIDIA NIM, OpenRouter, Ollama, LM Studio, and other OpenAI-compatible endpoints.

## Features

- **Provider Agnostic:** Easily switch between different LLM providers using a Registry pattern.
- **Autonomous Workflow:** Follows a structured Plan -> Design -> Execute -> Verify loop.
- **Isolated Workspace:** All agent operations are confined to the user-selected workspace directory, which defaults to `agent_workspace/`.
- **Persistent Memory:** Action history is saved to JSON for auditing and resumption.
- **Integrated Tools:** Built-in support for Python execution, Pytest, and Git.

## Prerequisites

- Python 3.10+
- API keys for NVIDIA NIM or OpenRouter, if using hosted providers
- Local LLM setup with Ollama or LM Studio, if using local providers
- Git, if you want to use Git actions
- Pytest, for test execution

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

   Example `.env`:

   ```env
   NIM_API_KEY=your_nvidia_nim_key_here
   OPENROUTER_API_KEY=your_openrouter_key_here
   LMSTUDIO_API_KEY=lm-studio
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
    base_url: http://localhost:11434

  lmstudio:
    model: local-model
    base_url: http://localhost:1234/v1
    api_key: lm-studio

  mock:
    model: mock-model
```

## Usage

Run the agent via the CLI:

```bash
python main.py --goal "Build a FastAPI ToDo API with SQLite" --provider openrouter
```

### Options

- `--goal`: The task for the agent to complete. This option is required.
- `--provider`: Override the default provider from `config/config.yaml`.
- `--fallback-provider`: Optional provider to use when the primary provider is rate-limited or temporarily unavailable. Fallback is attempted only if the current run has not executed workspace actions.
- `--max-steps`: Maximum autonomous execution steps. Default: `50`.
- `--workspace`: Name and location of the agent workspace directory. Defaults to `agent_workspace`.

### Selecting the Workspace

By default, Vibuilder creates and uses `agent_workspace` in the current directory.

Use `--workspace` to select a different folder name or location:

```bash
python main.py \
  --goal "Create a Python CLI calculator" \
  --workspace projects/calculator \
  --provider nim
```

An absolute path can also be used:

```bash
python main.py \
  --goal "Create a Python CLI calculator" \
  --workspace "/home/user/vibuilder-projects/calculator" \
  --provider nim
```

Windows PowerShell example:

```powershell
python main.py `
  --goal "Create a Python CLI calculator" `
  --workspace "D:\Vibuilder Projects\calculator" `
  --provider nim
```

All agent filesystem operations remain confined to the selected workspace.

### Automatic Provider Fallback

Vibuilder can optionally switch to another configured provider when the primary provider is rate-limited or temporarily unavailable.

Fallback is opt-in. Specify it with `--fallback-provider`:

#### Linux/macOS/Git Bash

```bash
python main.py \
  --goal "Create a Python CLI calculator and run its tests." \
  --provider openrouter \
  --fallback-provider nim \
  --max-steps 30
```

#### Windows PowerShell

```powershell
$goal = "Create a Python CLI calculator and run its tests."

python main.py `
  --goal $goal `
  --provider openrouter `
  --fallback-provider nim `
  --max-steps 30
```

Automatic fallback is attempted only when no new workspace actions have been executed during the current run. If the primary provider fails after creating or editing files, Vibuilder stops and preserves the current workspace instead of restarting the task with another provider.

The fallback provider must:
- be configured in `config/config.yaml`
- differ from the primary provider
- have any required API key available in `.env`
- be imported and registered with `ProviderRegistry`

Authentication failures do not trigger automatic fallback. Correct the provider credentials and rerun the command.

### Exit Codes

Vibuilder uses the following process exit codes:

- `0`: Task completed successfully.
- `1`: Unexpected application failure.
- `2`: Invalid command-line arguments.
- `3`: Unexpected fallback-provider creation or execution failure.
- `11`: Provider rate limit reached.
- `12`: Provider authentication failed.
- `13`: Provider temporarily unavailable.

## Example: Create and Upgrade a Python CLI Arithmetic Calculator

This example shows how an end user can use Vibuilder to first create a working Python CLI arithmetic calculator and then upgrade the existing calculator by adding percentage calculations.

Vibuilder writes and edits project files inside the isolated user-selected workspace directory (e.g. `agent_workspace/`).

Use this rule:

- For a **new project**, start with a clean workspace folder.
- For an **upgrade**, keep the existing workspace folder so Vibuilder can inspect and modify the current files.

### 1. Create a New CLI Arithmetic Calculator

First, remove any previous generated workspace if you want a fresh project.

#### Linux/macOS/Git Bash

```bash
rm -rf agent_workspace
```

#### Windows PowerShell

```powershell
Remove-Item -Recurse -Force agent_workspace -ErrorAction SilentlyContinue
```

Then run Vibuilder with a specific goal.

#### Linux/macOS/Git Bash

```bash
python main.py \
  --goal "Create a working Python CLI arithmetic calculator. Create calculator.py using argparse. Support add, subtract, multiply, divide, and power. Print only the result on success. Division by zero must produce a clear error and non-zero exit code. Add pytest tests in tests/test_calculator.py. Add README.md with usage examples. Run pytest before finishing." \
  --provider nim \
  --max-steps 30
```

#### Windows PowerShell

PowerShell uses the backtick character `` ` `` for multiline commands:

```powershell
python main.py `
  --goal "Create a working Python CLI arithmetic calculator. Create calculator.py using argparse. Support add, subtract, multiply, divide, and power. Print only the result on success. Division by zero must produce a clear error and non-zero exit code. Add pytest tests in tests/test_calculator.py. Add README.md with usage examples. Run pytest before finishing." `
  --provider nim `
  --max-steps 30
```

Alternatively, in PowerShell you can store the goal in a variable:

```powershell
$goal = "Create a working Python CLI arithmetic calculator. Create calculator.py using argparse. Support add, subtract, multiply, divide, and power. Print only the result on success. Division by zero must produce a clear error and non-zero exit code. Add pytest tests in tests/test_calculator.py. Add README.md with usage examples. Run pytest before finishing."

python main.py --goal $goal --provider nim --max-steps 30
```

Expected generated files:

```text
agent_workspace/
├── calculator.py
├── README.md
├── tests/
│   └── test_calculator.py
└── .vibuilder_memory.json
```

After Vibuilder finishes, verify the calculator manually:

```bash
python agent_workspace/calculator.py add 2 3
python agent_workspace/calculator.py subtract 10 4
python agent_workspace/calculator.py multiply 6 7
python agent_workspace/calculator.py divide 20 5
python agent_workspace/calculator.py power 2 8
```

Expected example outputs:

```text
5
6
42
4
256
```

Run the generated tests:

```bash
cd agent_workspace
pytest -q
```

### 2. Upgrade the Existing Calculator with Percentage Operations

To edit or upgrade an existing generated project, do **not** delete the workspace folder.

Use a goal that clearly tells Vibuilder to inspect and modify the current calculator instead of creating a brand-new one.

#### Linux/macOS/Git Bash

```bash
python main.py \
  --goal "Upgrade the existing Python CLI arithmetic calculator in agent_workspace by adding percentage calculations. Inspect the existing calculator.py, README.md, and tests first. Add support for percentage operations while preserving all existing add, subtract, multiply, divide, and power behavior. Implement these CLI operations: percent VALUE PERCENT, which returns PERCENT percent of VALUE; percent-of PART WHOLE, which returns what percentage PART is of WHOLE; add-percent VALUE PERCENT, which increases VALUE by PERCENT percent; subtract-percent VALUE PERCENT, which decreases VALUE by PERCENT percent. Validate division by zero for percent-of when WHOLE is zero. Update tests/test_calculator.py with pytest tests for the new percentage features and ensure all old tests still pass. Update README.md with usage examples. Run pytest before finishing." \
  --provider nim \
  --max-steps 40
```

#### Windows PowerShell

```powershell
$goal = "Upgrade the existing Python CLI arithmetic calculator in agent_workspace by adding percentage calculations. Inspect the existing calculator.py, README.md, and tests first. Add support for percentage operations while preserving all existing add, subtract, multiply, divide, and power behavior. Implement these CLI operations: percent VALUE PERCENT, which returns PERCENT percent of VALUE; percent-of PART WHOLE, which returns what percentage PART is of WHOLE; add-percent VALUE PERCENT, which increases VALUE by PERCENT percent; subtract-percent VALUE PERCENT, which decreases VALUE by PERCENT percent. Validate division by zero for percent-of when WHOLE is zero. Update tests/test_calculator.py with pytest tests for the new percentage features and ensure all old tests still pass. Update README.md with usage examples. Run pytest before finishing."

python main.py --goal $goal --provider nim --max-steps 40
```

After the upgrade, verify the original operations:

```bash
python agent_workspace/calculator.py add 2 3
python agent_workspace/calculator.py subtract 10 4
python agent_workspace/calculator.py multiply 6 7
python agent_workspace/calculator.py divide 20 5
python agent_workspace/calculator.py power 2 8
```

Then verify the new percentage operations:

```bash
python agent_workspace/calculator.py percent 200 15
python agent_workspace/calculator.py percent-of 30 200
python agent_workspace/calculator.py add-percent 200 15
python agent_workspace/calculator.py subtract-percent 200 15
```

Expected example outputs:

```text
30
15
230
170
```

Run the full test suite again:

```bash
cd agent_workspace
pytest -q
```

### 3. Recommended Backup Before Editing

Before asking Vibuilder to modify an existing project, you may want to create a backup.

#### Linux/macOS/Git Bash

```bash
cp -r agent_workspace agent_workspace_backup_before_edit
```

#### Windows PowerShell

```powershell
Copy-Item -Recurse agent_workspace agent_workspace_backup_before_edit
```

If Git is initialized in the workspace, you can also commit the working version before making changes:

```bash
cd agent_workspace
git add .
git commit -m "Working calculator before percentage upgrade"
cd ..
```

### 4. Tips for Better Results

Use clear, testable goals.

Good Vibuilder goals usually include:

- the files that should be created or edited,
- the required CLI behavior,
- expected error handling,
- test requirements,
- documentation requirements,
- an instruction to run tests before finishing.

Example goal:

```text
Upgrade the existing calculator. Preserve all current behavior. Add percent, percent-of, add-percent, and subtract-percent operations. Update tests and README. Run pytest before finishing.
```

When using PowerShell, avoid Unix-style line continuation with `\`.

Use one of these instead:

- a single-line command,
- the PowerShell backtick character `` ` ``,
- a `$goal` variable.

## Running Tests

Run the full test suite with:

```bash
PYTHONPATH=. pytest -q
```

On Windows PowerShell, if `PYTHONPATH=. pytest -q` does not work, use:

```powershell
$env:PYTHONPATH = "."
pytest -q
```

You can also run a syntax/import check with:

```bash
python -m compileall .
```

## Architecture

1. **Planner:** Breaks down the goal into a list of actionable steps.
2. **Architect:** Designs the system structure and file organization.
3. **Coder:** Executes the plan by generating code and performing file operations.
4. **Executor:** Runs the tools, including Filesystem, Python, Pytest, and Git, and returns feedback.
5. **Tester:** Evaluates test results and suggests fixes.
6. **Reviewer:** Provides a final assessment of the completed work.

### Agent Action Schema

The coder must return one JSON object per step.

Supported actions are:

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

All file paths must be relative to the user-selected workspace directory (which defaults to `agent_workspace/`).

Absolute paths and path traversal are rejected.

### Workspace Safety Model

All agent operations are confined to the user-selected workspace directory, which defaults to `agent_workspace/`.

The action validator rejects obvious unsafe paths such as absolute paths and `..` traversal. The workspace manager also resolves every path against the workspace root and rejects paths that escape the workspace.

## Testing with Mock Provider

You can test the framework without an API key using the `mock` provider:

```bash
python main.py --goal "Create a hello script" --provider mock --max-steps 5
```

The mock provider is useful for checking that the framework starts, creates files, executes actions, and writes memory without requiring an external LLM service.

## Notes on API Keys

Do not commit API keys to Git.

Store secrets in `.env`:

```env
NIM_API_KEY=your_nvidia_nim_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

The `.env` file should be ignored by Git.

Use `.env.example` to document required variables without exposing real credentials.
