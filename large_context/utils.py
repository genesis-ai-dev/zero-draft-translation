import os
import itertools
from collections import defaultdict
import re
import tiktoken

# dictionary that can be used by other script importing this script
passages = {
    'historical': [
        'acts 2:1',
        'acts 2:8',
    ],
    'prophetic': [
        'rev 6:1',
        'rev 6:8',
    ],
    'poetic': [
        'psa 23:1',
        'psa 23:6',
    ],
    'wisdom': [
        'jas 3:13',
        'jas 3:18',
    ],
    'gospel': [
        'luk 15:11',
        'luk 15:18',
    ],
    'epistle': [
        '1co 13:1',
        '1co 13:8',
    ],
    'apocalyptic': [
        'rev 21:1',
        'rev 21:8',
    ],
    'law': [
        'mat 5:17',
        'mat 5:24',
    ],
}

lang = {
    'Arabic': {
        'code': 'ara',
        'ebible': 'arb-arbnav',
        'target_file': {
            'Tamazight': 'resources/tmz/arb_tmz_verses.txt',
        },
    },
    'Tamazight': {
        'code': 'tmz',
        'ebible': '',
        'target_file': '',
    },
    'English': {
        'code': 'eng',
        'ebible': 'eng-eng-asv',
        'target_file': {
            'Tamazight': 'resources/tmz/eng_tmz_verses.txt',
        },
    },
}


def get_ngrams(text, n):
    words = text.split()
    return [' '.join(ngram) for ngram in itertools.chain(*[zip(*[words[i:] for i in range(j)]) for j in range(1, n+1)])]

def find_unique_ngrams(text, max_n):
    return set(get_ngrams(text, max_n))

def get_character_ngrams(text, n):
    return [''.join(ngram) for ngram in zip(*[text[i:] for i in range(n)])]

# def find_unique_ngrams(text, max_n):
#     ngrams = set()
#     for n in range(1, max_n + 1):
#         ngrams.update(get_character_ngrams(text, n))
#     return ngrams

def preprocess_text(text):
    # Remove punctuation and normalize whitespace
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', text)).strip()
    # For Arabic, we'll just normalize whitespace and remove diacritics
    # text = re.sub(r'\s+', ' ', text).strip()
    # return ''.join(char for char in text if not unicodedata.combining(char))

# def extract_lang_text(line, lang):
#     parts = line.split('__')
#     for part in parts:
#         if f'_{lang}‬' in part:
#             return part.split('‬', 1)[1].strip()
#     return ''  # Return empty string if language not found

def extract_lang_text(line, lang):
    # print(f"Extracting {lang} text from line: {line}")
    parts = line.split('__')
    for part in parts:
        if f'_{lang}' in part:
            # Split on the first occurrence of space after the language tag
            return part.split(' ', 1)[1].strip() if ' ' in part else ''
    return ''  # Return empty string if language not found



def find_relevant_context(all_lines, verse_to_translate, lang, max_n=4, max_number_closest_verses=100):
    verse_to_translate = preprocess_text(verse_to_translate)
    verse_ngrams = find_unique_ngrams(verse_to_translate, max_n)
    
    line_ngrams = []
    scores = [0] * len(all_lines)

    # Process all lines to get ngrams and calculate initial scores
    print(f"For verse: {verse_to_translate}")
    for i, line in enumerate(all_lines):
        lang_text = extract_lang_text(line, lang)
        processed_line = preprocess_text(lang_text)
        line_unique_ngrams = find_unique_ngrams(processed_line, max_n)
        line_ngrams.append(line_unique_ngrams)
        for ngram in line_unique_ngrams:
            if ngram in verse_ngrams:
                scores[i] += 1 / len(processed_line)
    
    # Print top 10 scores
    print("Top 10 scores:")
    for i, score in sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:10]:
        print(f"Line {i+1}: {all_lines[i].strip()[:100]}... with score {score}")
    
    relevant_lines = []
    known_ngrams = set()
    selected_indices = set()
    scores_reset = False
    
    while len(relevant_lines) < max_number_closest_verses:
        top_score_index = scores.index(max(scores))
        relevant_lines.append(all_lines[top_score_index])
        selected_indices.add(top_score_index)
        
        # Update known ngrams
        new_ngrams = line_ngrams[top_score_index] - known_ngrams
        known_ngrams.update(new_ngrams)
        
        # Print the ngrams contributed by the selected line which exist in the verse
        print(f"Line {len(relevant_lines)} ngrams: {line_ngrams[top_score_index] & verse_ngrams}")
        # Print the score of the selected line
        print(f"Line {len(relevant_lines)} score: {scores[top_score_index]}")
        
        # Set the score of the selected line to 0 to avoid reselection
        scores[top_score_index] = 0
        
        if not scores_reset:
            # Recalculate scores for all remaining lines
            for i, line_unique_ngrams in enumerate(line_ngrams):
                if i not in selected_indices:
                    new_score = sum(1 / len(extract_lang_text(all_lines[i], lang)) 
                                    for ngram in line_unique_ngrams 
                                    if ngram in verse_ngrams and ngram not in known_ngrams)
                    scores[i] = new_score
            
            # If all scores are zero, reset them to their initial values
            if all(score == 0 for score in scores):
                print("Resetting scores...")
                for i, unique_ngrams in enumerate(line_ngrams):
                    if i not in selected_indices:
                        score = sum(1 / len(extract_lang_text(all_lines[i], lang)) 
                                    for ngram in unique_ngrams 
                                    if ngram in verse_ngrams)
                        scores[i] = score
                scores_reset = True

    print(f"Found {len(relevant_lines)} relevant context lines.")
    print("Top 5 matching lines:")
    for i, line in enumerate(relevant_lines[:5], 1):
        print(f"{i}. {line.strip()[:100]}...")

    return '\n'.join(relevant_lines)




def read_files_to_string(path, file_extension='.txt', restricted_list=None):
    if restricted_list is None:
        restricted_list = []
    all_lines = []
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith(file_extension):
                file_path = os.path.join(path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        if not any(restricted in line for restricted in restricted_list):
                            all_lines.append(line)
    elif os.path.isfile(path) and path.endswith(file_extension):
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                if not any(restricted in line for restricted in restricted_list):
                    all_lines.append(line)
    return all_lines

def count_tokens(string):
    """Returns the number of tokens in a text string using tiktoken's specified encoding."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens