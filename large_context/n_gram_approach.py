import itertools
import string
from ScriptureReference import ScriptureReference
import pprint
import time
import re
import os
from datetime import datetime
pp = pprint.PrettyPrinter(indent=4)
REFERENCE = 0
CONTENT = 1

# ***************** PARAMETERS *****************

j = 4 # n-gram order
seed_size = 1000
start_verse = 'gen 1:1'
end_verse = 'rev 22:21'
ebible_filename = 'eng-engwmbb'
versification='eng'

# **********************************************

verses = ScriptureReference(start_verse, end_verse, bible_filename=ebible_filename, versification=versification).verses

# Passages is now a 2D list of [v_ref, verse_text] pairs

# remove empty verses
verses = [verse for verse in verses if verse[CONTENT] != '']

# verses = [
#     "In the beginning God created the heavens and the earth.",
#     "Now the earth was formless and empty, darkness was over the surface of the deep.",
#     "And the Spirit of God was hovering over the waters.",
#     # Add more verses as needed
# ]

# remove all punctuation from verses
verses = [[verse[REFERENCE], re.sub(r'[^a-z0-9 ]', '', verse[CONTENT].lower())] for verse in verses]

known_ngrams = []
seed_corpus = []
ngram_dict = {}
unique_ngrams = []

def get_ngrams(text, n):
    """Generate n-grams from a given text."""
    words = text.split()
    ngrams = list(itertools.chain(*[zip(*[words[i:] for i in range(j)]) for j in range(1, n+1)]))
    return [' '.join(ngram) for ngram in ngrams]

def find_unique_ngrams(verse, max_n):
    """Find unique n-grams up to the max_n order in the verse."""
    ngrams_set = set()
    for n in range(1, max_n + 1):
        ngrams_set.update(get_ngrams(verse, n))
    return list(ngrams_set)

# start time
start = time.time()

# get frequency count of all unique ngrams in corpus
# get all unique ngrams per verse
for i, verse in enumerate(verses):
    unique_verse_ngrams = find_unique_ngrams(verse[CONTENT], j)
    unique_ngrams.append(unique_verse_ngrams)
    for ngram in unique_verse_ngrams:
        if ngram not in ngram_dict:
            ngram_dict[ngram] = 1
        else:
            ngram_dict[ngram] += 1

# ngram_dict now has <unique_ngram: frequency_count> pairs 
# unique_ngrams now has list where elem i is list of unique ngrams for verse [i] 

# get sum of all ngram frequency counts for each verse
freq_count_sums = []
for i, verse in enumerate(verses):
    count = 0
    for ngram in unique_ngrams[i]:
        count += ngram_dict.get(ngram, 0)
    freq_count_sums.append(count / len(verse[CONTENT]))

# freq_count_sums [i] will have total ngram frequency count for verse [i]

known_ngrams = []
score_data = []
seed_time_data = []
for i in range(seed_size):
    seed_start = time.time()

    top_score_dropped = False
    init_entry = True
    
    # find the real top score
    while top_score_dropped or init_entry:
        init_entry, top_score_dropped = False, False
        top_score_index = freq_count_sums.index(max(freq_count_sums))
                
        # recalculate top score
        # for each unique ngram in the top-scoring verse, remove its score contribution if ngram is known
        for ngram in unique_ngrams[top_score_index]:
            if ngram in known_ngrams:
                freq_count_sums[top_score_index] -= ngram_dict.get(ngram, 0) / len(verses[top_score_index][CONTENT])
                while ngram in unique_ngrams[top_score_index]:
                    unique_ngrams[top_score_index].remove(ngram)
                top_score_dropped = True

    verse = verses[top_score_index]
    seed_corpus.append(verse)
    score_data.append(freq_count_sums[top_score_index])
    freq_count_sums[top_score_index] = 0
    known_ngrams += (unique_ngrams[top_score_index])
    seed_end = time.time()
    seed_time_data.append(seed_end - seed_start)
    
    # Print next highest verse
    print(f'{verse[REFERENCE]}: {verse[CONTENT]}', end="\n")
    # print percentage completion
    print(f"\rProgress: {i/seed_size*100:.2f}%", end="\r")

# end time
end = time.time()

# print total time taken
print("\nTime taken: {:.2f} seconds".format(end - start))

# Save the seed corpus to a file. 
if not os.path.exists('output'):
    os.makedirs('output')

# Format the current date/time to append to the filename
now = datetime.now()
date_time = now.strftime("%m-%d-%Y_%H-%M-%S")

# Prepend file content with j, seed_size, and seed_corpus verse range
file_content = f"j: {j}, seed_size: {seed_size}, seed_corpus verse range: {start_verse} - {end_verse}\n"
file_content += "\n".join([f"{verse[REFERENCE]}: {verse[CONTENT]}" for verse in seed_corpus])

# Create filename with date/time and prepend information
filename = f"output/{j}-gram_seed_size_{seed_size}_verse_range_{start_verse}-{end_verse}_{date_time}.txt".replace(':', '_')

# Write the seed corpus to the file
with open(filename, 'w') as f:
    f.write(file_content)

print(f"Seed corpus saved to output directory as {filename}")

# plot the scores
import matplotlib.pyplot as plt
fig1 = plt.figure(1)
plt.plot(score_data)
plt.ylabel('Score')
plt.xlabel('Seed')

# plot the time taken per seed
fig2 = plt.figure(2)
plt.plot(seed_time_data)
plt.ylabel('Time taken')
plt.xlabel('Seed')

plt.show()
