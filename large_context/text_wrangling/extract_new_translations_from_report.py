import json
import os

# Load the JSON data
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '../reports/eng to tmz report - 32-sample curriculum - claude-3-5-sonnet-20240620 3-gram - 2024-07-30 18_18_02.json')
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract BLEU scores and generated translations
bleu_scores = data['scores']['BLEU']['individual']
generated_translations = data['generated_translation']

# Ensure the lengths match
min_length = min(len(bleu_scores), len(generated_translations))
bleu_scores = bleu_scores[:min_length]
generated_translations = generated_translations[:min_length]

# Create a list of translations with BLEU score 0
zero_bleu_translations = []
for bleu, translation in zip(bleu_scores, generated_translations):
    if bleu == 0:
        zero_bleu_translations.append(translation)

# Write the translations to a file
output_file = os.path.join(current_dir, 'zero_bleu_translations.txt')
with open(output_file, 'w', encoding='utf-8') as f:
    for translation in zero_bleu_translations:
        f.write(f"{translation}\n")

print(f"Found {len(zero_bleu_translations)} translations with BLEU score 0.")
print(f"Translations written to '{output_file}'")