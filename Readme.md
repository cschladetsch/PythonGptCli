# GPT Code Exchange

A Python-based tool to interact with OpenAI's GPT-4 model via command-line or interactive mode.

## Features
- Accepts user input via command-line arguments or an interactive prompt.
- Uses OpenAI's GPT-4 model for generating responses.
- Color-coded output for better readability.
- Secure API key handling using environment variables.

---

## Requirements
- Python 3.6 or higher
- OpenAI Python package (`openai`)
- `termcolor` package for colored text

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/cschladetsch/GptCodeExchange.git
   cd GptCodeExchange
   ```

2. Install dependencies:
   ```bash
   pip3 install openai termcolor
   ```

---

## Configuration

### Set up the OpenAI API key:
- Add your OpenAI API key as an environment variable:
  ```bash
  export GPT_TOKEN="your_openai_api_key"
  ```

OR

- Place the key in a file named `token` in the same directory as `main.py`.

---

## Usage

### Command-Line Mode
Run the script with a prompt:
```bash
python3 main.py "What is the capital of Australia?"
```

### Interactive Mode
Start the script without arguments:
```bash
python3 main.py
```
Then type your prompt and press Enter:
```
> What is the capital of Australia?
< Canberra
```

### Exit Interactive Mode
Type `exit` or press `Ctrl+C`.

---

## Troubleshooting

1. **Error: `OpenAI.__init__() takes 1 positional argument but 2 were given`**
   - Ensure you are using the latest version of the `openai` package and have correctly set the API key.

2. **Environment Variable Not Found**
   - Verify that `GPT_TOKEN` is set. Check by running:
     ```bash
     echo $GPT_TOKEN
     ```

3. **Dependencies Missing**
   - Install them using:
     ```bash
     pip3 install openai termcolor
     ```

---

## License
This project is licensed under the MIT License.
