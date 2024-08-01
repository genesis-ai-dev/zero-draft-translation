import json
import matplotlib.pyplot as plt
import numpy as np
import os

# Load the JSON data
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '../reports/eng to tmz report - 32-sample curriculum - claude-3-5-sonnet-20240620 3-gram - 2024-07-30 18_18_02.json')
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract BLEU scores and n-gram scores
bleu_scores = data['scores']['BLEU']['individual']
ngram_scores = data['ngram_scores']

# Ensure the lengths match
min_length = min(len(bleu_scores), len(ngram_scores))
bleu_scores = bleu_scores[:min_length]
ngram_scores = ngram_scores[:min_length]

# Filter out points where BLEU score is 0
filtered_bleu_scores = []
filtered_ngram_scores = []
for bleu, ngram in zip(bleu_scores, ngram_scores):
    if bleu != 0:
        filtered_bleu_scores.append(bleu)
        filtered_ngram_scores.append(ngram)

# Create the scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(filtered_ngram_scores, filtered_bleu_scores, alpha=0.5)
plt.xlabel('N-gram Scores')
plt.ylabel('BLEU Scores')
plt.title('BLEU Scores vs N-gram Scores')

# Add a trend line
z = np.polyfit(filtered_ngram_scores, filtered_bleu_scores, 1)
p = np.poly1d(z)
plt.plot(filtered_ngram_scores, p(filtered_ngram_scores), "r--", alpha=0.8)

# Calculate correlation coefficient
correlation = np.corrcoef(filtered_ngram_scores, filtered_bleu_scores)[0, 1]
plt.text(0.05, 0.95, f'Correlation: {correlation:.2f}', transform=plt.gca().transAxes)

# Save the plot
output_path = os.path.join(current_dir, 'bleu_vs_ngram_scores.png')
plt.savefig(output_path)
plt.close()

print("Plot saved as 'bleu_vs_ngram_scores.png'")