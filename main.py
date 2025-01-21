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

try:
    api_key = read_token()
    client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"{Colors.RED}Error initializing OpenAI client: {str(e)}{Colors.RESET}")
    sys.exit(1)

def generate_response(prompt):
    """Generates a response using OpenAI's GPT-4 model."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
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

def show_history():
    """Displays query-response history from the log file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as history:
            colored_print(history.read(), "cyan")
    else:
        colored_print("No history found.", "yellow")

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

def interactive_mode():
    """Run in interactive mode with prompt."""
    load_history()
    spinner = Spinner()
    
    style = Style.from_dict({
        'prompt': '#0000ff',
    })

    try:
        bindings = KeyBindings()
        bindings.add("h")(lambda event: show_history())

        while True:
            try:
                user_prompt = prompt(
                    ANSI(Colors.BLUE + "> " + Colors.RESET),
                    key_bindings=bindings,
                    editing_mode=EditingMode.VI,
                    style=style
                )
                
                if user_prompt.lower() == "exit":
                    colored_print("Goodbye!", "cyan")
                    break
                elif user_prompt.lower() == "h":
                    show_history()
                    continue

                spinner.start()
                reply = generate_response(user_prompt)
                spinner.stop()

                print(f"{Colors.GREEN}< {Colors.RESET}{reply}")
                log_to_history(user_prompt, reply)

            except KeyboardInterrupt:
                spinner.stop()
                colored_print("\nSession terminated by user.", "cyan")
                break
            except Exception as e:
                spinner.stop()
                colored_print(f"Error: {e}", "red")

    except ImportError:
        colored_print("Falling back to standard input. Install prompt_toolkit for vi-like editing.", "red")
        while True:
            try:
                user_prompt = input(f"{Colors.BLUE}> {Colors.RESET}")
                if user_prompt.lower() == "exit":
                    colored_print("Goodbye!", "cyan")
                    break
                elif user_prompt.lower() == "h":
                    show_history()
                    continue

                spinner.start()
                reply = generate_response(user_prompt)
                spinner.stop()

                print(f"{Colors.GREEN}< {Colors.RESET}{reply}")
                log_to_history(user_prompt, reply)

            except KeyboardInterrupt:
                spinner.stop()
                colored_print("\nSession terminated by user.", "cyan")
                break
            except Exception as e:
                spinner.stop()
                colored_print(f"Error: {e}", "red")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Join all arguments into a single query
        query = " ".join(sys.argv[1:])
        process_single_query(query)
    else:
        interactive_mode()
