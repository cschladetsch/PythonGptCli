# Python GPT REPL

GPT Query Assistant is a versatile command-line tool that allows you to interact with OpenAI's GPT model in a highly functional and user-friendly way. Featuring color-coded output, a history log, and support for both single-command queries and REPL (Read-Eval-Print Loop) mode, this tool is perfect for quick interactions or extended conversations.

## Features

- **Color-Coded Output**:
  - User prompts are displayed in **blue**.
  - AI responses are shown in **green**.
  - Warnings and errors appear in **red**.
  - Logs and historical data are displayed in **cyan**.
- **Command-Line Queries**:
  - Pass a query directly as a command-line argument to get a response without entering REPL mode.
- **REPL Mode**:
  - Enter an interactive session where you can input multiple queries consecutively.
- **Query History**:
  - Logs all queries and responses to a file for later reference.
  - Display history directly in REPL mode using a shortcut (`h`).
- **Spinner Animation**:
  - Visual feedback during response generation.

## Prerequisites

- Python 3.7 or higher
- An OpenAI API key. Store it in a file named `~/.openai_gpt_token` or set it in the `OPENAI_API_KEY` environment variable.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Provide your OpenAI API key:

   - Save it in a file at `~/.openai_gpt_token`, or
   - Export it as an environment variable:
     ```bash
     export OPENAI_API_KEY=your_api_key
     ```

### Single-Command Query

Run the script with your query as a command-line argument:

```bash
$ python main.py Your query here
< answer
$ # To make it generally availble, add following to your startup script:
$ alias ask="python3 ~/path/to/main.py "
```

### REPL Mode

Start an interactive session:

```bash
$ python main.py
```

In REPL mode, you can:

- Type your queries and press Enter to get responses.
- Press `h` to display the query-response history.
- Type `exit` to end the session.

## Usage

```bash
$ ask
$ What is the capital of France?
> Paris
> h
[2025-01-21 10:00:00 UTC] QUERY: What is the capital of France?
[2025-01-21 10:00:00 UTC] RESPONSE: Paris
$ exit
$ ask 1+1
> 2
< exit # or just SIGINT (Ctrl-C)
$ 
```

## Dependencies

All required Python packages are listed in the `requirements.txt` file:

```plaintext
openai
termcolor
prompt_toolkit
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
