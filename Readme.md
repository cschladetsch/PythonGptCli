# Interactive GPT-4 Query Tool

This project is an interactive query tool that allows users to interact with GPT-4 through a command-line interface. It includes features such as a history log, customizable system prompts, and vi-like editing for commands.

---

## Features

1. **Interactive Query Mode**
   - Send queries to GPT-4 and get responses directly in the terminal.
   - Supports vi-style editing for user input.

2. **History Management**
   - Automatically logs queries and responses with UTC timestamps to `~/query_history.log`.
   - View the history using:
     - `h`: Show all history.
     - `h -N`: Show the last N queries and responses.

3. **Customizable System Prompt**
   - Modify the behavior of GPT-4 dynamically with the `set_system` command:
     - Example: `set_system You are a friendly and concise assistant.`

4. **Single Query Mode**
   - Pass a single query as a command-line argument to get a quick response without entering interactive mode.

5. **Enhanced Output Formatting**
   - Timestamps, queries, and responses are displayed in distinct colors for better readability.
     - **Timestamps**: Yellow
     - **Queries**: Cyan
     - **Responses**: Green

---

## Usage

### Installation
1. Clone the repository.
2. Ensure you have Python 3.7+ installed.
3. Install the required libraries:
   ```bash
   pip install prompt_toolkit openai
   ```

4. Set your OpenAI API key:
   - Place your API key in `~/.openai_gpt_token`, or set it as an environment variable:
     ```bash
     export OPENAI_API_KEY="your_api_key_here"
     ```

### Running the Tool

#### Interactive Mode
Run the script without arguments to enter the interactive mode:
```bash
python main.py
```
- Use `exit` to leave the session.
- Commands:
  - `h`: View all history.
  - `h -N`: View the last N entries in history.
  - `set_system <new system prompt>`: Update the system prompt dynamically.

#### Single Query Mode
Run the script with a query as an argument to get an immediate response:
```bash
python main.py "What is the capital of France?"
```

---

## File Structure

- `main.py`: Main script containing all functionality.
- `~/query_history.log`: Automatically generated log file for query history.

---

## Example

### Interactive Session
```bash
$ python main.py
> What is the weather today?
< It depends on your location. Can you specify?

> h -1
[2025-01-21 12:34:56 UTC] QUERY: What is the weather today?
[2025-01-21 12:34:56 UTC] RESPONSE: It depends on your location. Can you specify?

> set_system You are a weather assistant.
System prompt updated to: You are a weather assistant.

> Tell me about today's forecast.
< It looks like it will be sunny with a high of 25øC.

> exit
Goodbye!
```

---

## Customization
- Modify the default system prompt in the `InteractiveMode` class:
  ```python
  self.system_prompt = "You are a helpful assistant."
  ```
- Adjust colors in the `Colors` class.

---

## Notes
- Ensure your OpenAI API key is valid and has sufficient usage quota.
- The history log file (`~/query_history.log`) grows with usage; periodically archive or clean it if needed.
