# main.py
import sys
import os
from openai import OpenAI
from termcolor import colored

def read_token(file_path="token"):
    """Reads the API key from a file."""
    with open(file_path, "r") as file:
        return file.read().strip()

def get_token_from_environment():
    return os.getenv("GPT_TOKEN")

from openai import OpenAI

api_key = get_token_from_environment()
client = OpenAI(api_key=api_key)  # Correct import for OpenAI

from openai import OpenAI

client = OpenAI(api_key=api_key)  # Correct import for OpenAI

def generate_response(prompt):
    """Generates a response using OpenAI's GPT-4 model."""
    api_key = get_token_from_environment()
    if not api_key:
        raise ValueError("API key is not set. Please set the GPT_TOKEN environment variable.")

      # Set the API key for the session
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ])
    return response.choices[0].message.content

if __name__ == "__main__":
    # Check if arguments are passed
    if len(sys.argv) > 1:
        # Display argument list and exit
        #print(colored("Arguments detected:", "red"))
        for arg in sys.argv[1:]:
            print(colored(f"- {arg}", "yellow"))
        reply = generate_response(sys.argv[1:])
        print(colored("< ", "green") + reply)
        sys.exit()

    # Interactive mode
    while True:
        try:
            user_prompt = input(colored("> ", "blue"))
            if user_prompt.lower() == "exit":
                print(colored("Goodbye!", "cyan"))
                break
            reply = generate_response(user_prompt)
            print(colored("< ", "green") + reply)
        except KeyboardInterrupt:
            print(colored("\nSession terminated by user.", "cyan"))
            break
        except Exception as e:
            print(colored(f"Error: {e}", "red"))
