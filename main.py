import sys
import os
import json
import threading
import time
from datetime import datetime, timezone
from openai import OpenAI
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.styles import Style
import pyperclip

# File paths for history log and persistent items
HISTORY_FILE = os.path.expanduser("~/query_history.log")
ITEMS_FILE = os.path.expanduser("~/.ask_items.json")

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
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

def show_help():
    help_text = """
    - help or ?: Displays this help message.
    - h: Displays the query-response history.
    - quit: Exits the application.
    - list: Lists all available items.
    - add <value>: Adds a new item with an auto-incremented index.
    - remove <index>: Removes an item by its index.
    - up <file_path>: Uploads a file and sends its content to GPT for processing.
    - dl <file_path>: Saves clipboard content to <file_path>, backing up the previous file as <file_path>.last.
    """
    print(help_text)

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
    """Displays query-response history from the log file without timestamps."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as history:
            entries = history.read().strip().split("\n\n")
            if last_n:
                entries = entries[-last_n:]
            for entry in entries:
                lines = entry.strip().split("\n")
                for line in lines:
                    if "QUERY:" in line:
                        query = line.split("QUERY:")[1].strip()
                        colored_print(f"QUERY: {query}", "cyan")
                    elif "RESPONSE:" in line:
                        response = line.split("RESPONSE:")[1].strip()
                        colored_print(f"RESPONSE: {response}", "green")
    else:
        colored_print("No history found.", "yellow")

def upload_file_to_gpt(file_path):
    """
    Reads the file content and sends it to the GPT session.
    """
    spinner = Spinner()
    try:
        spinner.start()
        with open(file_path, "r") as file:
            file_content = file.read()

        # Add the file content to the GPT prompt
        upload_prompt = (
            f"Uploaded file: {os.path.basename(file_path)}\n\n"
            f"File Content:\n{file_content[:2000]}..."  # Truncate if needed
        )

        # Generate response
        response = generate_response(upload_prompt)
        spinner.stop()
        colored_print(response, "green")
        log_to_history(f"File uploaded: {file_path}", response)

    except Exception as e:
        spinner.stop()
        colored_print(f"Error uploading file: {str(e)}", "red")

def save_clipboard_to_file(file_path):
    """Saves the clipboard content to the specified file, creating a backup of the previous file."""
    try:
        content = pyperclip.paste()
        if not content:
            colored_print("Clipboard is empty.", "yellow")
            return

        # Backup the existing file
        if os.path.exists(file_path):
            backup_path = f"{file_path}.last"
            os.rename(file_path, backup_path)
            colored_print(f"Backup created: {backup_path}", "cyan")

        # Save clipboard content to the file
        with open(file_path, "w") as file:
            file.write(content)
        colored_print(f"Clipboard content saved to {file_path}", "green")

    except Exception as e:
        colored_print(f"Error saving clipboard content: {str(e)}", "red")

class InteractiveMode:
    def __init__(self):
        self.spinner = Spinner()
        self.style = Style.from_dict({
            'prompt': '#0000ff',
        })
        self.bindings = KeyBindings()
        self.system_prompt = "You are a helpful assistant."
        self.items = self.load_items()

    def load_items(self):
        """Load items from the persistent storage file."""
        if os.path.exists(ITEMS_FILE):
            with open(ITEMS_FILE, "r") as f:
                return json.load(f)
        return []

    def save_items(self):
        """Save the current items to the persistent storage file."""
        with open(ITEMS_FILE, "w") as f:
            json.dump(self.items, f, indent=4)

    def handle_exit(self):
        colored_print("Goodbye!", "cyan")

    def handle_file_upload(self, user_prompt):
        try:
            file_path = user_prompt.split("up ", 1)[1].strip()
            if os.path.exists(file_path):
                upload_file_to_gpt(file_path)
            else:
                colored_print("File not found. Please check the path.", "red")
        except IndexError:
            colored_print("Invalid command. Use 'up <file_path>'.", "red")

    def handle_list(self):
        if self.items:
            colored_print("Items:", "cyan")
            for index, value in enumerate(self.items):
                colored_print(f"{index}: {value}", "green")
        else:
            colored_print("No items found.", "yellow")

    def handle_add(self, user_prompt):
        try:
            value = user_prompt.split("add ", 1)[1].strip()
            if value:
                self.items.append(value)
                self.save_items()
                colored_print(f"Added: {len(self.items) - 1} -> {value}", "green")
            else:
                colored_print("No value provided. Use 'add <value>'.", "red")
        except IndexError:
            colored_print("Invalid command. Use 'add <value>'.", "red")

    def handle_remove(self, user_prompt):
        try:
            index = int(user_prompt.split("remove ", 1)[1].strip())
            if 0 <= index < len(self.items):
                removed_item = self.items.pop(index)
                self.save_items()
                colored_print(f"Removed: {index} -> {removed_item}", "green")
            else:
                colored_print(f"Invalid index: {index}", "red")
        except (IndexError, ValueError):
            colored_print("Invalid command. Use 'remove <index>'.", "red")

    def handle_download(self, user_prompt):
        try:
            file_path = user_prompt.split("dl ", 1)[1].strip()
            save_clipboard_to_file(file_path)
        except IndexError:
            colored_print("Invalid command. Use 'dl <file_path>'.", "red")

    def handle_history(self):
        show_history()

    def process_input(self, user_prompt):
        if user_prompt.lower() == "exit":
            self.handle_exit()
            return False
        elif user_prompt.startswith("up "):
            self.handle_file_upload(user_prompt)
            return True
        elif user_prompt in ["help", "?"]:
            show_help()
            return True
        elif user_prompt == "list":
            self.handle_list()
            return True
        elif user_prompt == "h":
            self.handle_history()
            return True
        elif user_prompt.startswith("add "):
            self.handle_add(user_prompt)
            return True
        elif user_prompt.startswith("remove "):
            self.handle_remove(user_prompt)
            return True
        elif user_prompt.startswith("dl "):
            self.handle_download(user_prompt)
            return True
        else:
            # Handle conversational queries
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
        spinner = Spinner()
        try:
            spinner.start()
            reply = generate_response(query)
            spinner.stop()
            print(f"{Colors.GREEN}< {Colors.RESET}{reply}")
        except Exception as e:
            spinner.stop()
            colored_print(f"Error: {str(e)}", "red")
    else:
        interactive = InteractiveMode()
        interactive.run()
