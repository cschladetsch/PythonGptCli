# GPT Code Exchange

A Python-based tool for interacting with OpenAI's GPT-4 model. This project allows users to send queries and receive responses while maintaining a history of interactions.

## Features
- Interactive querying interface with spinner for waiting periods.
- Query and response history stored with UTC timestamps.
- Scroll through history using arrow keys.
- `vi`-like editing support (if `prompt_toolkit` is installed).
- Supports history display (`h` command) and logs all interactions.

---

## Requirements
- Python 3.12 or higher
- Required Python packages:
  - `openai`
  - `termcolor`
  - `prompt_toolkit`

---

## Installation

### Using a Virtual Environment (Recommended)
1. Create a virtual environment:
   ```bash
   python3 -m venv ~/venvs/gpt_env
