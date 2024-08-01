import os
from dotenv import load_dotenv
import time
from ScriptureReference import ScriptureReference
from Model import Model
import re
from utils import passages, lang, read_files_to_string, extract_lang_text, find_relevant_context, waha_curriculum
from TranslationMetric import TranslationMetric
import traceback
import anthropic

#*******************************PARAMETERS*************************************

model_api = "anthropic" # or "openai" | "anthropic"
model_name = "claude-3-5-sonnet-20240620" # "gpt-4o" | "claude-3-5-sonnet-20240620" | 
number_closest_verses = 32 # Number of verse examples to provide to the model
max_ngram = 3 # Maximum n-gram length to consider for context matching
genre = "historical" # options: historical, prophetic, poetic, wisdom, gospel, epistle, apocalyptic, law (see utils.py)
source_lang = "English" # see utils.py for available languages
target_lang = "Tamazight" # see utils.py for available languages
perform_translation = True # If False, only calculate and report n-gram scores without translation

# Curriculum parameters
curriculum = False # If True, use waha_curriculum; if False, use genre
start_verse = "gen 1:1" # Starting verse for curriculum

#******************************************************************************

parallel_file = lang[source_lang]['target_file'][target_lang]
ebible_source = lang[source_lang]['ebible']
source_code = lang[source_lang]['code']
target_code = lang[target_lang]['code']

model = Model(api=model_api, model_name=model_name)

# Function to get verses based on curriculum or genre
def get_verses_to_translate():
    if curriculum:
        all_verses = []
        all_references = []
        start_index = next((i for i, ref_pair in enumerate(waha_curriculum) if ref_pair[0] == start_verse), 0)
        for ref_pair in waha_curriculum[start_index:]:
            start, end = ref_pair
            print(start, end)
            verses = ScriptureReference(start, end, bible_filename=ebible_source).verses
            all_verses.extend([verse[1] for verse in verses])
            all_references.extend([verse[0] for verse in verses])
        return all_verses, all_references
    else:
        start, end = passages[genre][0], passages[genre][1]
        verses = ScriptureReference(start, end, bible_filename=ebible_source).verses
        return [verse[1] for verse in verses], [verse[0] for verse in verses]

verses, references = get_verses_to_translate()
print('References (restricted list)\n', references)

# Get example translation pairs for context (exclude lines to be translated)
directory_path = os.path.join(os.path.abspath(''), parallel_file)
all_lines = read_files_to_string(directory_path, restricted_list=references)
print("First 5 lines:")
for line in all_lines[:5]:
    print(line.strip())

evaluator = TranslationMetric(
    model_name=model_name,
    samples_per_translation=number_closest_verses,
    source_code=source_code,
    target_code=target_code, 
    genre=genre if not curriculum else "curriculum",
    max_ngram=max_ngram,
)

# Get date, time for the report filename
from datetime import datetime
now = datetime.now()
dt_string = now.strftime("%Y-%m-%d %H:%M:%S").replace(":","_")

# Generate report path
report_dir = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(report_dir, exist_ok=True)
report_path = os.path.join(report_dir, f"{source_code} to {target_code} report - {number_closest_verses}-sample {'curriculum' if curriculum else genre} - {model_name} {max_ngram}-gram - {dt_string}.json")

# Initialize the report
evaluator.initialize_report(report_path)

start_time = time.perf_counter()  # Start time

for i, (verse, reference) in enumerate(zip(verses, references)):
    try:
        closest_verses, ngram_scores = find_relevant_context(all_lines, verse, lang=source_code, max_n=max_ngram, max_number_closest_verses=number_closest_verses)
        
        ngram_score_sum = sum(ngram_scores)
        
        if perform_translation:
            translated_text = model.translate(
                source_lang=source_lang,
                target_lang=target_lang,
                closest_verses=closest_verses,
                verse=verse
            )
            
            print(f"Verse to translate {i+1}:")
            print(verse)
            print(f"Translation for verse {i+1}:")
            print(translated_text)
            
            # Retrieve gold standard translation
            gold_standard = next((extract_lang_text(line.strip(), target_code) for line in open(parallel_file, 'r', encoding='utf-8') if f'{reference}_' in line), "No reference translation available")
            
            print(f"Gold standard translation for verse {i+1}: ")
            print(gold_standard)
        else:
            translated_text = "Translation not performed"
            gold_standard = "Translation not performed"
        
        print(f"N-gram score sum for verse {i+1}: {ngram_score_sum}")
        print("\n---\n")
        
        # Update the report with this verse's translation and n-gram score
        evaluator.update_report(verse, translated_text, gold_standard, reference, ngram_score_sum)
        
    except anthropic.InternalServerError:
        print(f"Internal server error occurred for verse {i+1}. Retrying in 60 seconds...")
        time.sleep(60)
        i -= 1  # Retry this verse
        continue
    except Exception as e:
        print(f"An error occurred while processing verse {i+1}:")
        print(traceback.format_exc())
        print("Continuing with the next verse...\n")
        evaluator.update_report(verse, "Error occurred", "Error occurred", reference, 0)

end_time = time.perf_counter()
print(f"Time taken: {end_time - start_time} seconds")

# Finalize the report
evaluator.finalize_report()

print(f"Report generated and saved to {report_path}")
