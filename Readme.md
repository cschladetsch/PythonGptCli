# GPT Command-Line Assistant

This script provides a command-line assistant that interacts with OpenAI's GPT-4 to handle various tasks such as managing a list of items, uploading files, and engaging in conversational queries.

---

## Features

### Core Commands
- `help` or `?`: Displays a list of available commands.
- `exit`: Exits the program.
- `list`: Lists all items with their base-0 index.
- `add <value>`: Adds a new item with an auto-incremented index.
- `remove <index>`: Removes an item by its base-0 index.
- `up <file_path>`: Uploads a file and sends its content to GPT for processing.

### Interactive Capabilities
- Engage in a natural conversation with GPT-4.
- Store and recall user data (e.g., user-defined lists).
- Persistent storage using a JSON file at `~/.ask_items.json`.

---

## File Structure

- **`main.py`**: The main program.
- **`~/.ask_items.json`**: Persistent storage for user-defined lists.
- **`~/query_history.log`**: Log file for all queries and responses.

---

## Requirements

- Python 3.8 or later
- Installed packages:
  - `openai`
  - `prompt_toolkit`

---

## Installation

1. Clone this repository or download the `main.py` file.
2. Install dependencies:
   ```bash
   pip install openai prompt_toolkit
   ```
3. Ensure you have an OpenAI API key saved in `~/.openai_gpt_token` or set as an environment variable `OPENAI_API_KEY`.

---

## Usage

### Running the Script
```bash
python main.py
```

### Example Interaction
```bash
> help
- help: Displays this help message.
- quit: Exits the application.
- list: Lists all available items.
- add <value>: Adds a new item with an auto-incremented index.
- remove <index>: Removes an item by its index.
- up <file_path>: Uploads a file and processes it with GPT.

> add Buy groceries
Added: 0 -> Buy groceries

> list
Items:
0: Buy groceries

> remove 0
Removed: 0 -> Buy groceries

> up example.txt
< Response from GPT about the uploaded file >

> exit
Goodbye!
```

---

## Troubleshooting

### Common Issues
1. **Missing API Key**:
   - Ensure your API key is saved in `~/.openai_gpt_token` or exported as an environment variable:
     ```bash
     export OPENAI_API_KEY="your_api_key"
     ```

2. **Corrupted `~/.ask_items.json`**:
   - If the persistent file is corrupted, delete it:
     ```bash
     rm ~/.ask_items.json
     ```

3. **Dependencies Not Installed**:
   - Reinstall missing packages:
     ```bash
     pip install -r requirements.txt
     ```

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.
