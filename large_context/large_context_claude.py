import anthropic
import os
from dotenv import load_dotenv
import tiktoken
import time
from ScriptureReference import ScriptureReference
import re
import itertools
from collections import defaultdict
from TranslationMetric import TranslationMetric

def get_ngrams(text, n):
    words = text.split()
    return [' '.join(ngram) for ngram in itertools.chain(*[zip(*[words[i:] for i in range(j)]) for j in range(1, n+1)])]

def find_unique_ngrams(text, max_n):
    return set(get_ngrams(text, max_n))

def preprocess_text(text):
    # Remove punctuation and normalize whitespace
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', text)).strip()

def find_relevant_context(all_lines, verse_to_translate, max_n=4, max_context_lines=100):
    verse_to_translate = preprocess_text(verse_to_translate)
    verse_ngrams = find_unique_ngrams(verse_to_translate, max_n)
    
    ngram_dict = defaultdict(int)
    line_ngrams = []
    
    # Process all lines to get ngrams and their frequencies
    for line in all_lines:
        processed_line = preprocess_text(line)
        line_unique_ngrams = find_unique_ngrams(processed_line, max_n)
        line_ngrams.append(line_unique_ngrams)
        for ngram in line_unique_ngrams:
            ngram_dict[ngram] += 1
    
    # Calculate initial scores for each line
    scores = [sum(ngram_dict[ngram] for ngram in unique_ngrams) / len(line) 
              for unique_ngrams, line in zip(line_ngrams, all_lines)]
    
    relevant_lines = []
    known_ngrams = set()
    
    verse_count = 0
    while len(relevant_lines) < max_context_lines and verse_ngrams - known_ngrams:
        top_score_index = scores.index(max(scores))
        relevant_lines.append(all_lines[top_score_index])
        
        # Update known ngrams and recalculate score for the selected line
        new_ngrams = line_ngrams[top_score_index] - known_ngrams
        known_ngrams.update(new_ngrams)
        
        for ngram in new_ngrams:
            for i, line_unique_ngrams in enumerate(line_ngrams):
                if ngram in line_unique_ngrams:
                    scores[i] -= ngram_dict[ngram] / len(all_lines[i])
        
        scores[top_score_index] = 0  # Ensure this line isn't selected again
        verse_count += 1
    
    if len(relevant_lines) >= max_context_lines:
        print(f"Reached max context lines: {max_context_lines}")
    else:
        print(f"All vocabulary in the target verse acquired in {verse_count} verses.")
    
    return '\n'.join(relevant_lines)

def read_files_to_string(path, file_extension='.txt'):
    all_lines = []
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith(file_extension):
                file_path = os.path.join(path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    all_lines.extend(file.readlines())
    elif os.path.isfile(path) and path.endswith(file_extension):
        with open(path, 'r', encoding='utf-8') as file:
            all_lines.extend(file.readlines())
    return all_lines

def count_tokens(string):
    """Returns the number of tokens in a text string using tiktoken's specified encoding."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens

# Usage example:
directory_path = os.path.join(os.path.abspath(''), 'resources', 'tmz', 'arb_tmz_verses_trimmed.txt')
all_lines = read_files_to_string(directory_path)
print(f'number of lines in resource files: {len(all_lines)}')

print(f'The number of tokens in the text is: {count_tokens("".join(all_lines))}')

load_dotenv()
client = anthropic.Anthropic(
    api_key=os.getenv('ANTHROPIC_API_KEY'),
)

start_time = time.perf_counter()  # Start time

verses = ScriptureReference("1pe 1:1", '1pe 1:5', bible_filename='arb-arbnav').verses
# Get 2nd element of each verse
verses = [verse[1] for verse in verses]

with open('resources/tmz/gold/tmz_1PE_1_1-5.txt', 'r', encoding='utf-8') as file:
    reference_translations = [re.sub(r'[\u202B\u202C]', '', line.strip()) for line in file if line.strip()]
generated_translations = [] 

evaluator = TranslationMetric(model_name="Claude-3-5-sonnet", version="20240620")

for i, verse in enumerate(verses):
    relevant_context = find_relevant_context(all_lines, verse, max_context_lines=10)
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        system=f"You are an expert at translation and can perfectly apply the translation principles demonstrated in these Arabic to Tamazight resources:\n{relevant_context}",
        messages=[
            {
                "role": "user",
                "content": f"Translate the following into the Tamazight language with Arabic script (NOT Tifinagh script): \n{verse}"
            }
        ]
    )
    
    # Print relevant context lines and the verse to translate
    print(f"Relevant context for verse {i+1}:")
    print(relevant_context)
    print(f"Verse to translate {i+1}:")
    print(verse)

    print(f"Translation for verse {i+1}:")
    translation = re.search('\u202b(.*?)\u202c', message.content[0].text)
    translated_text = translation.group(1) if translation else "Translation not found"
    print(translated_text)
    print("\n---\n")

    generated_translations.append(translated_text)
    # Reference translations already loaded from file

end_time = time.perf_counter()
print(f"Time taken: {end_time - start_time} seconds")

# Evaluate translations
results = evaluator.compare_translations(generated_translations, reference_translations)

# Print overall scores
for metric, score in results.items():
    print(f"{metric} overall score: {score.overall}")

# Show bleu score of 2nd line
print(f"BLEU score for 2nd line: {results['BLEU'].individual[1]}")

# Show overall chrF score
print(f"chrF overall score: {results['chrF'].overall}")

# Generate and save the report
evaluator.generate_report("translation_evaluation_report.json")