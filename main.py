# main.py
import sys
import os
import threading
import itertools
import time
from datetime import datetime, timezone
from openai import OpenAI
from termcolor import colored
import readline
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.enums import EditingMode

# File path for history log
HISTORY_FILE = os.path.expanduser("~/query_history.log")

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

api_key = read_token()
client = OpenAI(api_key=api_key)

def load_history():
    """Loads history from the log file into readline."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as history:
            for line in history:
                if line.startswith("[") and "QUERY:" in line:
                    query = line.split("QUERY:")[1].strip()
                    readline.add_history(query)

def generate_response(prompt):
    """Generates a response using OpenAI's GPT-4 model."""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def spinner():
    """Displays a spinner while waiting for the API response."""
    for char in itertools.cycle('|/-\\'):
        if not spinner_active:
            break
        sys.stdout.write(colored(f"\r{char} Thinking...", "yellow"))
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r")  # Clear spinner line

def log_to_history(prompt, response):
    """
    Logs the query and response to a history file with a UTC timestamp.
    Ensures the log directory and file exist.
    """
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
            print(colored(history.read(), "cyan"))
    else:
        print(colored("No history found.", "yellow"))

if __name__ == "__main__":
    # Load history into readline
    load_history()

    # Set vi editing mode using prompt_toolkit
    try:
        bindings = KeyBindings()
        bindings.add("h")(lambda event: show_history())

        while True:
            try:
                user_prompt = prompt(
                    colored("> ", "blue"),
                    key_bindings=bindings,
                    editing_mode=EditingMode.VI,
                )
                if user_prompt.lower() == "exit":
                    print(colored("Goodbye!", "cyan"))
                    break
                elif user_prompt.lower() == "h":
                    show_history()
                    continue

                spinner_active = True
                spinner_thread = threading.Thread(target=spinner)
                spinner_thread.start()

                reply = generate_response(user_prompt)

                spinner_active = False
                spinner_thread.join()

                print(colored("< ", "green") + reply)

                # Log to history file
                log_to_history(user_prompt, reply)
            except KeyboardInterrupt:
                print(colored("\nSession terminated by user.", "cyan"))
                break
            except Exception as e:
                print(colored(f"Error: {e}", "red"))

    except ImportError:
        print(colored("Falling back to standard input. Install prompt_toolkit for vi-like editing.", "red"))
        while True:
            try:
                user_prompt = input(colored("> ", "blue"))
                if user_prompt.lower() == "exit":
                    print(colored("Goodbye!", "cyan"))
                    break
                elif user_prompt.lower() == "h":
                    show_history()
                    continue

                spinner_active = True
                spinner_thread = threading.Thread(target=spinner)
                spinner_thread.start()

                reply = generate_response(user_prompt)

                spinner_active = False
                spinner_thread.join()

                print(colored("< ", "green") + reply)

                # Log to history file
                log_to_history(user_prompt, reply)
            except KeyboardInterrupt:
                print(colored("\nSession terminated by user.", "cyan"))
                break
            except Exception as e:
                print(colored(f"Error: {e}", "red"))
