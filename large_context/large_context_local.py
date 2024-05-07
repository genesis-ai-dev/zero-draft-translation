from openai import OpenAI 
from ScriptureReference import ScriptureReference
import os

def read_files_to_string(directory, file_extension='.txt'):
    combined_content = ""
    for filename in os.listdir(directory):
        if filename.endswith(file_extension):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                combined_content += file.read() + "\n"  # Appends a newline after each file's content
    return combined_content

# Usage example:
directory_path = os.path.join(os.path.abspath(''), 'dictionary')
all_text = read_files_to_string(directory_path)

# print(len(all_text))



client = OpenAI(
    base_url='http://localhost:1234/v1',
    api_key='not needed',
)

scripture = ScriptureReference('gen 1:1', end_ref='Genesis 2:1')
print(scripture.verses)

translations = []

for verse in scripture.verses:
    completion = client.chat.completions.create(
        model='local_model',
        messages=[
            {'role': 'system', 'content': f'You understand the language of the following translations: {all_text}'},
            {'role': 'user', 'content': f'After giving your reasoning and rationale, simply write the translation of the following in square brackets: "{verse}"'},
        ],
        temperature=0,
    )

    print(completion.choices[0].message.content)

    # Append the translation of the mesage which is found in the square brackets
    translation = completion.choices[0].message.content.split('[')[1].split(']')[0]
    translations.append(translation)

[print(translation) for translation in translations]