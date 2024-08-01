import json
import re
import os
import pyperclip

def extract_verse_ranges(json_data):
    verse_ranges = []
    seen_ranges = set()

    for item in json_data:
        if item['setId'].startswith(('01', '03')):
            for lesson in item['lessons']:
                if 's' in lesson and lesson['s']:
                    for s in lesson['s']:
                        if isinstance(s, str) and re.match(r'^[A-Z1-3]{3}\.\d+\.\d+-[A-Z1-3]{3}\.\d+\.\d+$', s):
                            start, end = s.split('-')
                            start_book, start_chapter, start_verse = start.split('.')
                            end_book, end_chapter, end_verse = end.split('.')
                            
                            start_ref = f"{start_book.lower()} {start_chapter}:{start_verse}"
                            end_ref = f"{end_book.lower()} {end_chapter}:{end_verse}"
                            
                            if (start_ref, end_ref) not in seen_ranges:
                                verse_ranges.append([start_ref, end_ref])
                                seen_ranges.add((start_ref, end_ref))

    return merge_overlapping_ranges(verse_ranges)

def merge_overlapping_ranges(ranges):
    # Sort ranges based on the start verse
    sorted_ranges = sorted(ranges, key=lambda x: get_verse_index(x[0]))
    merged = []

    for range in sorted_ranges:
        if not merged or get_verse_index(range[0]) > get_verse_index(merged[-1][1]):
            merged.append(range)
        else:
            merged[-1][1] = max(merged[-1][1], range[1], key=get_verse_index)

    return merged

def get_verse_index(verse_ref):
    book, chapter, verse = re.match(r'(\w+) (\d+):(\d+)', verse_ref).groups()
    with open(os.path.join(os.path.dirname(__file__), '..', 'vref_eng.txt'), 'r') as f:
        for i, line in enumerate(f):
            if line.strip() == f"{book.upper()} {chapter}:{verse}":
                return i
    return -1

# Read and parse the JSON data
with open(os.path.join(os.path.dirname(__file__), 'wahaSets.json'), 'r') as f:
    json_data = json.load(f)

# Extract and process verse ranges
result = extract_verse_ranges(json_data)

# Print the result
print(json.dumps(result, indent=2))

# Use pyperclip to copy the result to the clipboard
pyperclip.copy(json.dumps(result, indent=2))