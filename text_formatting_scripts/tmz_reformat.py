import os
import re

def extract_verses(input_directory, output_directory):
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # List all the .SFM files in the input directory
    files = [f for f in os.listdir(input_directory) if f.endswith('.SFM')]
    
    for file in files:
        input_path = os.path.join(input_directory, file)
        output_path = os.path.join(output_directory, os.path.splitext(file)[0] + '_cleaned.txt')

        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            for line in infile:
                # Match lines that start with \v followed by a space and digits (the verse number)
                if re.match(r'\\v \d+', line):
                    # Remove everything up to the first space after the verse number
                    verse_text = re.sub(r'^\\v \d+ ', '', line)
                    
                    # Correctly remove all sections marked by \tag …\tag* and fix the order
                    tag_pattern = r'\\(\w+) .*?\\\1\*'
                    while re.search(tag_pattern, verse_text):
                        for tag_match in re.finditer(tag_pattern, verse_text):
                            tag_content = tag_match.group(0)
                            tag_start, tag_end = tag_match.span()
                            # Replace the content with placeholder to maintain order
                            verse_text = verse_text[:tag_start] + "\n" + verse_text[tag_end:]
                    
                    # Remove any remaining Roman characters and backslashes
                    verse_text = re.sub(r'[a-zA-Z\\]+', '', verse_text)
                    
                    # Reorder the segments properly
                    parts = verse_text.split('\n')
                    verse_text = ''.join(parts[::-1])  # Reverse the order of parts
                    
                    # Write the cleaned verse to the output file
                    outfile.write(verse_text.strip() + '\n')

# Example usage:
# Assuming you have the directories set up, call the function like this:
extract_verses('C:/Users/No code/Tamazight/text', 
               'C:/Users/No code/Tamazight/text/output')

# Note: Paths need to be adjusted to your actual directory structure.

