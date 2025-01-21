import sys
import os
import threading
import itertools
import time
from datetime import datetime, timezone
from openai import OpenAI
import readline
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.styles import Style

# File path for history log
HISTORY_FILE = os.path.expanduser("~/query_history.log")

# ANSI color codes
class Colors:
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'
    RED = '\033[31m'
    RESET = '\033[0m'

def colored_print(text, color):
    """Print colored text using ANSI escape sequences"""
    color_code = getattr(Colors, color.upper(), Colors.RESET)
    print(f"{color_code}{text}{Colors.RESET}")

def read_token(file_path="~/.openai_gpt_token"):
    """
    Reads the API key from a file if it exists; otherwise, retrieves it from an environment variable.
    """
    file_path = os.path.expanduser(file_path)
    if "OPENAI_API_KEY" in os.environ:
        return os.environ["OPENAI_API_KEY"]
    elif os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read().strip()
    else:
        raise FileNotFoundError("Token file not found and 'OPENAI_API_KEY' environment variable is not set.")

# Initialize the OpenAI client globally
try:
    api_key = read_token()
    client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"{Colors.RED}Error initializing OpenAI client: {str(e)}{Colors.RESET}")
    sys.exit(1)

def generate_response(prompt, system_prompt="You are a helpful assistant."):
    """Generates a response using OpenAI's GPT-4 model."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

class Spinner:
    def __init__(self):
        self.active = False
        self.thread = None

    def spin(self):
        while self.active:
            for char in '|/-\\':
                if not self.active:
                    break
                sys.stdout.write(f'\r{Colors.YELLOW}{char} Thinking...{Colors.RESET}')
                sys.stdout.flush()
                time.sleep(0.1)
        sys.stdout.write('\r' + ' ' * 20 + '\r')
        sys.stdout.flush()

    def start(self):
        self.active = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def stop(self):
        self.active = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * 20 + '\r')
        sys.stdout.flush()

def log_to_history(prompt, response):
    """Logs the query and response to a history file with a UTC timestamp."""
    log_dir = os.path.dirname(HISTORY_FILE)
    os.makedirs(log_dir, exist_ok=True)

    with open(HISTORY_FILE, "a") as history:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        history.write(f"[{timestamp}] QUERY: {prompt}\n")
        history.write(f"[{timestamp}] RESPONSE: {response}\n\n")

def show_history(last_n=None):
    """Displays query-response history from the log file with colored timestamps, queries, and responses."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as history:
            entries = history.read().strip().split("\n\n")
            if last_n:
                entries = entries[-last_n:]
            for entry in entries:
                lines = entry.strip().split("\n")
                for line in lines:
                    if line.startswith("[") and "QUERY:" in line:
                        query = line.split("QUERY:")[1].strip()
                        colored_print(f"QUERY: {query}", "cyan")
                    elif line.startswith("[") and "RESPONSE:" in line:
                        response = line.split("RESPONSE:")[1].strip()
                        colored_print(f"RESPONSE: {response}", "green")
    else:
        colored_print("No history found.", "yellow")

def get_nth_history_line(n):
    """Retrieve the Nth query from the history file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as history:
            queries = [line.split("QUERY: ", 1)[-1].strip()
                       for line in history if "QUERY: " in line]
            if 1 <= n <= len(queries):
                return queries[n - 1]
            else:
                return None
    return None

def process_single_query(query):
    """Process a single query and exit."""
    spinner = Spinner()
    try:
        spinner.start()
        reply = generate_response(query)
        spinner.stop()
        print(reply)
        log_to_history(query, reply)
    except Exception as e:
        spinner.stop()
        print(f"{Colors.RED}Error: {str(e)}{Colors.RESET}")
    finally:
        spinner.stop()

class InteractiveMode:
    def __init__(self):
        self.spinner = Spinner()
        self.style = Style.from_dict({
            'prompt': '#0000ff',
        })
        self.bindings = KeyBindings()
        self.system_prompt = "You are a helpful assistant."

    def handle_exit(self):
        colored_print("Goodbye!", "cyan")

    def handle_history(self, user_prompt):
        if user_prompt.strip() == "h":
            show_history()
        elif user_prompt.startswith("h -"):
            try:
                n = int(user_prompt.split("-", 1)[1])
                if n > 0:
                    show_history(last_n=n)
                else:
                    colored_print("Invalid number of queries to show.", "red")
            except ValueError:
                colored_print("Invalid command format. Use 'h' or 'h -N'.", "red")

    def handle_system_prompt(self, user_prompt):
        try:
            new_prompt = user_prompt.split("set_system ", 1)[1].strip()
            self.system_prompt = new_prompt
            colored_print(f"System prompt updated to: {new_prompt}", "green")
        except IndexError:
            colored_print("Invalid command format. Use 'set_system <new system prompt>'.", "red")

    def handle_nth_query(self, user_prompt):
        try:
            n = int(user_prompt[1:])
            nth_query = get_nth_history_line(n)
            if nth_query:
                colored_print(f"Editing Query {n}: {nth_query}", "yellow")
                return prompt(
                    f"{Colors.BLUE}[Edit Query] > {Colors.RESET}",
                    default=nth_query,
                    editing_mode=EditingMode.VI,
                    style=self.style
                )
            else:
                colored_print(f"No query at index {n}.", "red")
                return None
        except ValueError:
            colored_print("Invalid command. Use !N where N is a number.", "red")
            return None

    def process_input(self, user_prompt):
        if user_prompt.lower() == "exit":
            self.handle_exit()
            return False
        elif user_prompt.startswith("h"):
            self.handle_history(user_prompt)
            return True
        elif user_prompt.startswith("set_system"):
            self.handle_system_prompt(user_prompt)
            return True
        elif user_prompt.startswith("!"):
            edited_prompt = self.handle_nth_query(user_prompt)
            if edited_prompt:
                user_prompt = edited_prompt
            else:
                return True

        self.spinner.start()
        reply = generate_response(user_prompt, self.system_prompt)
        self.spinner.stop()

        print(f"{Colors.GREEN}< {Colors.RESET}{reply}")
        log_to_history(user_prompt, reply)
        return True

    def run(self):
        try:
            while True:
                user_prompt = prompt(
                    ANSI(Colors.BLUE + "> " + Colors.RESET),
                    editing_mode=EditingMode.VI,
                    style=self.style
                )
                if not self.process_input(user_prompt):
                    break
        except KeyboardInterrupt:
            self.spinner.stop()
            colored_print("\nSession terminated by user.", "cyan")
        except Exception as e:
            self.spinner.stop()
            colored_print(f"Error: {e}", "red")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Join all arguments into a single query
        query = " ".join(sys.argv[1:])
        process_single_query(query)
    else:
        interactive = InteractiveMode()
        interactive.run()
