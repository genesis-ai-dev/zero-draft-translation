import sys
from   langchain.llms import LlamaCpp
import os
import requests
from fuzzywuzzy import fuzz
import matplotlib.pyplot as plt
from itertools import islice

from DSPyMix import Mix

mix = Mix(compile=True)

def dspy_generate_new_verse(verses):
    # Generate a new verse based on three incoming
    new_verse = mix.module(verse_ver_1=verses[0], verse_ver_2=verses[1], verse_ver_3=verses[2])
    # new_verse = mix.module(verse=verses[0])
    print(new_verse.mixed_verse)
    return new_verse

def download_bible_text(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()

def calculate_levenshtein(reference_verses, new_verse):
    return [fuzz.ratio(new_verse, ref) / 100 for ref in reference_verses]

urls = [
    'https://raw.githubusercontent.com/BibleNLP/ebible/main/corpus/eng-englsv.txt',
    'https://raw.githubusercontent.com/BibleNLP/ebible/main/corpus/eng-engylt.txt',
    'https://raw.githubusercontent.com/BibleNLP/ebible/main/corpus/eng-engwebster.txt'
]

bibles = [download_bible_text(url) for url in urls]

assert all(len(bible) == len(bibles[0]) for bible in bibles), "Bibles are not the same length."

new_verses = []
lev_distances = []

cap = 100
for verses in islice(zip(*bibles), cap):
    new_verse = dspy_generate_new_verse(verses)
    new_verses.append(new_verse.mixed_verse)
    distances = calculate_levenshtein(verses, new_verse.mixed_verse)
    lev_distances.append(distances)

# Save the new verses to a filemap
with open("new_bible_abacusai_girafe_sentence_xfmr.txt", "w") as file:
    for verse in new_verses:
        file.write(verse + "\n")

# Print Levenshtein distances
for idx, distances in enumerate(zip(*lev_distances)):
    print(f"Verse {idx + 1} Distances: {distances}")

# Plotting Levenshtein distances
plt.figure(figsize=(12, 6))
for idx, distances in enumerate(zip(*lev_distances)):
    plt.plot(range(len(distances)), distances, label=f'Version {idx + 1} Distance')
plt.xlabel('Verse Number')
plt.ylabel('Levenshtein Distance')
plt.legend()
plt.title('Levenshtein Distance of New Verses from Originals')
plt.show()