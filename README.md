# LangGraph Mini-Assistant

A tiny, modular assistant built on **LangGraph** + **LangChain** that can:
- route any input into _question_, _code_, or _text_ workflows,
- generate or edit code/text with a Google Gemini model,
- save results to files (`output.py`/`output.js`/… or `output.txt`).

The project exposes a simple CLI loop and a reusable `graph_builder()` you can import in other apps.

---

## Features

- **Routing**: A small LLM router classifies input as a question, code, or text.
- **Workflows**:
  - **Question → Answer** (Q&A with LLM)
  - **Code**: generate _or_ edit code, then **save to a file**
  - **Text**: generate _or_ edit text, then **save to `output.txt`**
- **Pluggable nodes**: Provide your own node implementations by passing a custom module to `graph_builder(impl_module=...)`.

---

## Project Structure

```
.
├─ main.py        # CLI: compiles the graph and runs a simple REPL
├─ graph.py       # graph_builder(): constructs the LangGraph StateGraph
└─ nodes.py       # Node implementations (LLM prompts, save-to-disk helpers, routers)
<img width="3840" height="3452" alt="Untitled diagram _ Mermaid Chart-2025-08-21-204540" src="https://github.com/user-attachments/assets/09699f02-ba4d-4948-8118-3a0d82439e1c" />

```

---

## Requirements

- Python **3.10+**
- Packages (install via `pip -r requirements.txt`):
  - `langgraph`
  - `langchain`
  - `langchain-google-genai`
  - `python-dotenv`

> You can pin exact versions as needed for your environment.

---

## Environment Variables

Create a `.env` file in the project root with your Google Generative AI key:

```
GOOGLE_API_KEY=your_api_key_here
```

`nodes.py` loads `.env` and the `langchain-google-genai` integration reads `GOOGLE_API_KEY` automatically.

---

## Quick Start

```bash
# 1) Create & activate a virtual environment (Windows example)
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux:
# python3 -m venv .venv
# source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Add your .env with GOOGLE_API_KEY
# 4) Run the app
python main.py
```

You’ll see a prompt. Type a **question**, **some code**, or **plain text** and the graph will route and process it.
Press `Ctrl+C` to exit.

---

## How It Works (High Level)

### Graph builder
`graph_builder()` wires nodes and edges for three flows:
- **Question flow**: `START → router → question → answer → END`
- **Code flow**: `START → router → code → code_router → (generate_code|edit_code) → save_code → END`
- **Text flow**: `START → router → text → text_router → (generate_text|edit_text) → save_text → END`

### Nodes
Implemented in `nodes.py` using LangChain prompts + Gemini:
- `question` – Q&A prompt
- `generate_code` / `edit_code`
- `generate_text` / `edit_text`
- `save_code` – writes LLM output to a language-appropriate filename (`output.py`, `output.js`, etc.); defaults to `output.py`
- `save_text` – writes to `output.txt`
- `router`, `code_router`, `text_router` – classify what to do next

---

## Programmatic Use

You can import the graph and reuse it in your own Python app:

```python
from graph import graph_builder

# Optionally pass a custom module with your own node functions
# e.g., import my_nodes; builder = graph_builder(impl_module=my_nodes)
builder = graph_builder()
graph = builder.compile()

# Invoke with a state dict
result = graph.invoke({"query": "Write a Python function that prints 1..5"})
print(result)
```

**Custom nodes**: Implement functions with the same names as in `nodes.py`
(`question`, `generate_code`, etc.) and pass your module via `impl_module=...`.

---

## State & Outputs

- Input state key: `query` (string)
- Nodes may add keys like `answer`, `generate_code`, `edit_code`, `generate_text`, `edit_text`.
- Final nodes:
  - **`save_code`** → writes a file (e.g., `output.py`) in the current working directory
  - **`save_text`** → writes `output.txt`

The CLI prints the returned keys/values for transparency.

---

## Examples

- **Ask a question**:  
  `How do I center a div with CSS?` → routes to **question → answer**

- **Generate code**:  
  `Write a Node.js script to read a JSON file and print its keys` → **generate_code → save_code**

- **Edit code**:  
  `Fix this: prnit("Hello")` → **edit_code → save_code** (will correct and save)

- **Generate text**:  
  `Напиши абзац о возобновляемой энергетике` → **generate_text → save_text**

- **Edit text**:  
  `Fix grammar: Hi my name are Maria` → **edit_text → save_text**

---

## Troubleshooting

- **No API key / auth errors**: ensure `.env` contains a valid `GOOGLE_API_KEY` and the environment is activated.
- **File not saved**: check current working directory permissions; `save_code`/`save_text` write next to the script.
- **Routing looks wrong**: try giving more explicit instructions (e.g., “Edit this code:” before pasting code).
