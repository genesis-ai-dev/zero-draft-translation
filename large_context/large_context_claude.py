import anthropic
import os
from dotenv import load_dotenv
import tiktoken
import time

def read_files_to_string(directory, file_extension='.txt'):
    combined_content = ""
    for filename in os.listdir(directory):
        # if filename.endswith(file_extension):
        if 'combined_verses_training' in filename:
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                combined_content += file.read() + "\n"  # Appends a newline after each file's content
    return combined_content

def remove_last_n_lines(text, n):
    lines = text.splitlines()  # Split the string into lines
    if len(lines) > n:
        lines = lines[:-n]  # Remove the last n lines
    else:
        lines = []  # If there are fewer than n lines, return an empty string
    return '\n'.join(lines)  # Join the remaining lines back into a string

def count_tokens(string):
    """Returns the number of tokens in a text string using tiktoken's specified encoding."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens

# Usage example:
directory_path = os.path.join(os.path.abspath(''), 'dictionary', 'tmz')
all_text = read_files_to_string(directory_path)
all_text = remove_last_n_lines(all_text, 10000)

print(f'The number of tokens in the text is: {count_tokens(all_text)}')

load_dotenv()
client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv('ANTHROPIC_API_KEY'),
)

start_time = time.perf_counter()  # Start time

message = client.messages.create(
    model="claude-3-opus-20240229",
    # model="claude-3-haiku-20240307",
    max_tokens=1000,
    temperature=0,
    system=f"You are an expert at translation and can perfectly apply the translation principles demonstrated in these English to Tamazight resources:\n{all_text}",
    # system=f"You are an expert at translating from English into Tamazight with Arabic script.",

    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """Translate the following into Tamazight with Arabic script (NOT Tifinagh): \"
                       So the LORD left those nations, without driving them out hastily. He didn’t deliver them into Joshua’s hand.
                    """
                }
            ]
        }
    ]
)
print(message.content)

end_time = time.perf_counter()  # End time
print(f"Time taken: {end_time - start_time} seconds")