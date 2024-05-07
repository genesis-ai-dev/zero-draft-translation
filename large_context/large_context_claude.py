import anthropic
import os
from dotenv import load_dotenv
import tiktoken

def read_files_to_string(directory, file_extension='.txt'):
    combined_content = ""
    for filename in os.listdir(directory):
        if filename.endswith(file_extension):
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
directory_path = os.path.join(os.path.abspath(''), 'dictionary')
all_text = read_files_to_string(directory_path)
reduced_text = remove_last_n_lines(all_text, 6000)

print(f'The number of tokens in the text is: {count_tokens(reduced_text)}')

load_dotenv()
client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv('ANTHROPIC_API_KEY'),
)

message = client.messages.create(
    # model="claude-3-sonnet-20240229",
    model="claude-3-haiku-20240307",
    max_tokens=1000,
    temperature=0,
    system=f"You are an expert at translation and can perfectly apply the translation principles demonstrated in these resources:\n{reduced_text}",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Translate: \"In the beginning God created the heavens and the earth.\""
                }
            ]
        }
    ]
)
print(message.content)