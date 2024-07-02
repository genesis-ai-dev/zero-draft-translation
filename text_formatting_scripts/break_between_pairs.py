

def add_breaks_between_lines(input_file: str, output_file: str):
    """
    Reads text from an input file, adds a blank line between every two lines, and writes the result to an output file.

    :param input_file: Path to the input file containing the original text.
    :param output_file: Path to the output file where the modified text will be saved.
    """
    try:
        # Open the input file and read the contents
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Prepare a list to collect the modified lines
        modified_lines = []
        
        # Iterate over the lines
        for i in range(0, len(lines), 2):
            # Append the first line of the pair, stripping any trailing newline characters
            modified_lines.append(lines[i].strip())
            # Check if there is a second line in this pair
            if i + 1 < len(lines):
                modified_lines.append(lines[i + 1].strip())
            # Add a blank line to separate the pairs
            modified_lines.append('')  # This adds a blank line

        # Join all the modified lines back into a single string with newlines
        modified_text = '\n'.join(modified_lines)

        # Open the output file and write the modified text
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(modified_text)
    
    except Exception as e:
        print(f"Error processing files: {e}")

add_breaks_between_lines('dictionary/quran_english_target.txt', 'dictionary/quran_english_target_with_breaks.txt')