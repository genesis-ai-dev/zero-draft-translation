import os
import json
from bs4 import BeautifulSoup

def parse_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    entry = {}

    # Main word
    lx = soup.find('div', class_='lx')
    if lx:
        entry['word'] = lx.get_text(strip=True)

    # Main word definitions and examples
    psGroup = soup.find('div', class_='psGroup')
    if psGroup:
        # Extract part of speech from the class name
        ps_classes = psGroup.find('div', {'class': 'ps'}).get('class', [])
        part_of_speech = next((ps_class.split('_')[-1] for ps_class in ps_classes if 'ps_' in ps_class), None)
        entry['part_of_speech'] = part_of_speech
        
        gl = psGroup.find('div', class_='gl')
        if gl:
            entry['definition'] = gl.get_text(strip=True)
        exGroup = psGroup.find('div', class_='exGroup')
        if exGroup:
            ex = exGroup.find('div', class_='ex')
            if ex:
                entry['example'] = ex.get_text(strip=True)
            tr = exGroup.find('div', class_='tr')
            if tr:
                entry['translation'] = tr.get_text(strip=True)

    # Derivatives
    entry['derivatives'] = []
    for ldGroup in soup.find_all('div', class_='ldGroup'):
        derivative = {}
        ld = ldGroup.find('div', class_='ld')
        if ld:
            derivative['word'] = ld.get_text(strip=True)
        # Extract part of speech from the class name for derivatives
        ps_classes = ldGroup.find('div', {'class': 'ps'}).get('class', [])
        part_of_speech = next((ps_class.split('_')[-1] for ps_class in ps_classes if 'ps_' in ps_class), None)
        derivative['part_of_speech'] = part_of_speech
        
        co = ldGroup.find('div', class_='co')
        if co:
            derivative['definition'] = co.get_text(strip=True)
        entry['derivatives'].append(derivative)

    return entry


def parse_directory(directory_path):
    entries = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.html'):
            entry = parse_html(os.path.join(directory_path, filename))
            entries.append(entry)
    return entries

# Change this to the path where your HTML files are located
directory_path = 'C:/Users/caleb/Bible Translation Project/No code/mrw/mrw/dict/lexicon'

# Parse the directory and save to JSON
dictionary_entries = parse_directory(directory_path)

# Write the JSON output to a file
with open('mrw_dictionary.json', 'w', encoding='utf-8') as json_file:
    json.dump(dictionary_entries, json_file, ensure_ascii=False, indent=4)

print(f"Parsing complete. Entries saved to /path/to/save/your/output.json")
