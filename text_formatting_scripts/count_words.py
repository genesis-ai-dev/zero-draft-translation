import re
from collections import defaultdict
import os

def count_words_in_files(file_paths):
    # Dictionary to store word counts for each file
    word_counts = defaultdict(int)
    
    # Regular expression to match words (groups of alphabet characters)
    word_pattern = re.compile(r'[a-zA-Z]+')

    # Iterate over each file path provided
    for file_path in file_paths:
        try:
            # Open and read the file
            with open(file_path, 'r') as file:
                content = file.read()
                # Find all words in the file content
                words = word_pattern.findall(content)
                # Count the words
                word_counts[file_path] += len(words)
        except FileNotFoundError:
            print(f"Error: The file {file_path} does not exist.")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return word_counts

# Example usage:
file_list = [
    os.path.join(os.path.abspath(''), 'dictionary', 'target_training_dataset_joined.txt'),
    os.path.join(os.path.abspath(''), 'dictionary', 'quran_english_target_joined.txt'),
    os.path.join(os.path.abspath(''), 'dictionary', 'target_dictionary.txt'),
]
result = count_words_in_files(file_list)
print(result)
