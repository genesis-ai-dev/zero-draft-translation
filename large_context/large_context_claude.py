import os
from dotenv import load_dotenv
import time
from ScriptureReference import ScriptureReference
from Model import Model
import re
from utils import *
from TranslationMetric import TranslationMetric

#*******************************PARAMETERS*************************************

model_api = "anthropic" # or "openai" | "anthropic"
model_name = "claude-3-5-sonnet-20240620" # "gpt-4o" | "claude-3-5-sonnet-20240620" | 
number_closest_verses = 32 # Number of examples to provide to the model
max_ngram = 3 # Maximum n-gram length to consider for context matching
genre = "gospel" # options: historical, prophetic, poetic, wisdom, gospel, epistle, apocalyptic, law (see utils.py)
source_lang = "English"
target_lang = "Tamazight"

#******************************************************************************

parallel_file = lang[source_lang]['target_file'][target_lang] # __source [------] __target [------] examples
ebible_source = lang[source_lang]['ebible'] # Containing verses to be translated
source_code = lang[source_lang]['code'] # code found in parallel file
target_code = lang[target_lang]['code'] # code found in parallel file

model = Model(api=model_api, model_name=model_name)

start, end = passages[genre][0], passages[genre][1]
# Get verses to translate
raw_verses = ScriptureReference(start, end, bible_filename=ebible_source).verses
# Get 2nd element of each verse
verses = [verse[1] for verse in raw_verses]
references = [verse[0] for verse in raw_verses]
print('References (restricted list)\n', references)

# Get example translation pairs for context (exclude lines to be translated)
directory_path = os.path.join(os.path.abspath(''), parallel_file)
all_lines = read_files_to_string(directory_path, restricted_list=references)
# Print the first 5 lines
print("First 5 lines:")
for line in all_lines[:5]:
    print(line.strip())

start_time = time.perf_counter()  # Start time

evaluator = TranslationMetric(
    model_name=model_name,
    samples_per_translation=number_closest_verses,
    source_code=source_code,
    target_code=target_code, 
    genre=genre,
    max_ngram=max_ngram,
)

# Retrieve gold standard verses from file
with open(parallel_file, 'r', encoding='utf-8') as file:
    reference_translations = [extract_lang_text(line.strip(), target_code) for line in file if any(f'{ref}_' in line for ref in references)]
generated_translations = [] 

for i, verse in enumerate(verses):
    closest_verses = find_relevant_context(all_lines, verse, lang=source_code, max_n=max_ngram, max_number_closest_verses=number_closest_verses)
    
    translated_text = model.translate(
        source_lang=source_lang,
        target_lang=target_lang,
        closest_verses=closest_verses,
        verse=verse
    )
    
    # Print relevant context lines and the verse to translate
    print(f"Closest verses to verse {i+1}:")
    print(closest_verses)
    print(f"Verse to translate {i+1}:")
    print(verse)

    print(f"Translation for verse {i+1}:")
    print(translated_text)
    print(f"Gold standard translation for verse {i+1}: ")
    print(reference_translations[i])
    print("\n---\n")

    generated_translations.append(translated_text)
    # Reference translations already loaded from file

end_time = time.perf_counter()
print(f"Time taken: {end_time - start_time} seconds")

# Print all reference and generated translations
print("Reference translations:")
for ref in reference_translations:
    print(ref)
print("\n---\n")
print("Generated translations:")
for gen in generated_translations:
    print(gen)
print("\n---\n")

# Evaluate translations
results = evaluator.compare_translations(generated_translations, reference_translations, references)

# Print overall scores
for metric, score in results.items():
    print(f"{metric} overall score: {score.overall}")

# get date, time
from datetime import datetime
now = datetime.now()
dt_string = now.strftime("%Y-%m-%d %H:%M:%S").replace(":","_")

# Generate and save the report
# Create report subdirectory if it doesn't exist
report_dir = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(report_dir, exist_ok=True)

# Save the report to the report subdirectory
report_path = os.path.join(report_dir, f"{source_code} to {target_code} report - {number_closest_verses}-sample {genre} - {model_name} {max_ngram}-gram - {dt_string}.json")
evaluator.generate_report(report_path)
