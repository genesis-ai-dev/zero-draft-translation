from ScriptureReference import ScriptureReference

def parse_reference(ref):
    # Split the reference into its components (book, chapter, verse)
    # print(f"Reference: {ref}")
    parts = ref.split('_')
    chapter_verse = parts[1].split(':')
    # Filter out non-digit characters for chapter and verse numbers
    chapter = ''.join([char for char in chapter_verse[0] if char.isdigit()])
    verse = ''.join([char for char in chapter_verse[1] if char.isdigit()])
    return (parts[0], int(chapter), int(verse))

def combine_verses(eng_verses, tmz_verses):
    eng_dict = {parse_reference(v[0]): v[1] for v in eng_verses}
    tmz_dict = {parse_reference(v[0]): v[1] for v in tmz_verses}
    combined = []

    # All unique verse references from both lists
    all_refs = set(eng_dict.keys()) | set(tmz_dict.keys())

    null_text = 'عفاون سغدات ئي واوال اد'

    for ref in sorted(all_refs):
        if ref in eng_dict and ref in tmz_dict:  # Check if there is a match in both dictionaries
            eng_content = eng_dict[ref]
            tmz_content = tmz_dict[ref]
            ref_formatted = f"{ref[0]}_{ref[1]}:{ref[2]}"
            if tmz_content == null_text:
                continue
            # combined.append(f"{ref_formatted}_eng {eng_content} {ref_formatted}_tmz {tmz_content}")
            combined.append(f"__{ref_formatted}_eng {eng_content} \u202A__{ref_formatted}_tmz\u202C \u202B{tmz_content}\u202C")

    return combined

# Load verses from ScriptureReference
ebible_verses = ScriptureReference('Gen 1:1', 'Rev 22:21', 'eng-eng-asv').verses
# remove all elements where the verse is empty
ebible_verses = [verse for verse in ebible_verses if verse[0] != '']
tmz_verses = ScriptureReference('Gen 1:1', 'Rev 22:21', 'C:/Users/caleb/Bible Translation Project/No code/Tamazight/text', 'usfm').verses

combined_verses = combine_verses(ebible_verses, tmz_verses)

# Write the verses to a file
output_path = 'C:/Users/caleb/Bible Translation Project/No code/Tamazight/text/output/eng_tmz_verses_new.txt'
with open(output_path, 'w', encoding='utf-8') as outfile:
    for verse in combined_verses:
        outfile.write(verse + '\n')
