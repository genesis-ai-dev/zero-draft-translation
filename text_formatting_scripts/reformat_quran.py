import re

def remove_newlines_except_before_numbers(input_file, output_file):
    # Open the input file and read its content
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Use regular expression to find all newline characters not followed by a number
    # and replace them with an empty string
    modified_content = re.sub(r'\n(?![0-9])', '', content)
    
    # Write the modified content to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(modified_content)

# Example usage:
input_file_name = 'dictionary/quran_english_formatted_1.txt' # Replace with your input file's name
output_file_name = 'dictionary/quran_english_formatted_2.txt' # Replace with your desired output file's name

remove_newlines_except_before_numbers(input_file_name, output_file_name)


def remove_lines_with_words(input_file, output_file, words_to_remove):
    # Open the input file and the output file
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        # Iterate over each line in the input file
        for line in infile:
            # Check if the line contains any of the words to remove
            if not any(word.lower() in line.lower() for word in words_to_remove):
                # If none of the words to remove are in the line, write it to the output file
                outfile.write(line)

# Example usage:
# input_file_name = 'dictionary/quran_yusuf.txt' # Replace with your input file's name
# output_file_name = 'dictionary/quran_english_formatted_1.txt' # Replace with your desired output file's name
# words_to_remove = ['chapter', 'surah'] # List of words you want to remove lines for

# remove_lines_with_words(input_file_name, output_file_name, words_to_remove)


def format_lines_with_sequence(input_file, output_file):
    main_sequence = 1
    sub_sequence = 0
    previous_number = 0

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # Use regular expression to find and exclude the first number in the line
            match = re.match(r'^(\d+)\s*(.*)', line)
            if match:
                current_number = int(match.group(1))
                rest_of_line = match.group(2)
                # Check if the sequence should reset
                if current_number <= previous_number:
                    main_sequence += 1
                    sub_sequence = 1
                else:
                    sub_sequence += 1
            else:
                # If no number is found at the start, skip this line or handle as needed
                continue

            # Update the previous number for the next iteration
            previous_number = current_number

            # Write the formatted line, excluding the original starting number, to the output file
            formatted_line = f"{main_sequence:03d}.{sub_sequence:03d} {rest_of_line}\n"
            outfile.write(formatted_line)

# Example usage
# input_file_name = 'dictionary/quran_maranao_formatted_1.txt'  # Replace with your input file's name
# output_file_name = 'dictionary/quran_maranao_formatted_2.txt'  # Replace with your desired output file's name

# format_lines_with_sequence(input_file_name, output_file_name)
