# main.py
import sys
import os
import threading
import itertools
import time
from openai import OpenAI
from termcolor import colored

def read_token(file_path="token"):
    """
    Reads the API key from a file if it exists; otherwise, retrieves it from an environment variable.
    """
    if "OPENAI_API_KEY" in os.environ:
        return os.environ["OPENAI_API_KEY"]
    elif os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read().strip()
    else:
        raise FileNotFoundError("Token file not found and 'OPENAI_API_KEY' environment variable is not set.")

api_key = read_token()
client = OpenAI(api_key=api_key)

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

if __name__ == "__main__":
    # Check if arguments are passed
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            print(colored(f"- {arg}", "yellow"))
        reply = generate_response(" ".join(sys.argv[1:]))
        print(colored("< ", "green") + reply)
        sys.exit()

    # Interactive mode
    while True:
        try:
            user_prompt = input(colored("> ", "blue"))
            if user_prompt.lower() == "exit":
                print(colored("Goodbye!", "cyan"))
                break
            
            spinner_active = True
            spinner_thread = threading.Thread(target=spinner)
            spinner_thread.start()

            reply = generate_response(user_prompt)

            spinner_active = False
            spinner_thread.join()

            print(colored("< ", "green") + reply)
        except KeyboardInterrupt:
            print(colored("\nSession terminated by user.", "cyan"))
            break
        except Exception as e:
            print(colored(f"Error: {e}", "red"))
