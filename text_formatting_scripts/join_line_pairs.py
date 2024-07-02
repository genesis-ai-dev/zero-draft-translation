def merge_lines(input_file_path: str, output_file_path: str):
    """
    Reads a text file, merges every pair of lines into a single line, and writes the results to a new file.

    :param input_file_path: Path to the input text file.
    :param output_file_path: Path to the output text file where the merged lines will be saved.
    """
    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile, \
             open(output_file_path, 'w', encoding='utf-8') as outfile:
            lines = infile.readlines()

            # Process every pair of lines
            for i in range(0, len(lines), 2):
                # Safely get the next line if it exists
                next_line = lines[i+1].strip() if i+1 < len(lines) else ''
                # Write the merged line to the output file
                outfile.write(lines[i].strip() + " " + next_line + '\n')

    except FileNotFoundError:
        print(f"Error: The file '{input_file_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
merge_lines('dictionary/target_training_dataset_pairs.txt', 'dictionary/target_training_dataset_joined.txt')
