def format_text_lines_to_file(input_file, tag1, tag2, split_index, output_file):
    # Read lines from the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    # Ensure lines are stripped of newline characters
    lines = [line.strip() for line in lines]
    
    # Split lines into two groups
    group1 = lines[:split_index]
    group2 = lines[split_index:]
    
    # Check if both groups have equal number of lines, if not, adjust
    min_length = min(len(group1), len(group2))
    group1 = group1[:min_length]
    group2 = group2[:min_length]
    
    # Open the output file and write the formatted lines
    with open(output_file, 'w') as file:
        for i, (line1, line2) in enumerate(zip(group1, group2), start=1):
            file.write(f"sentence {i} - {tag1}: {line1}\n")
            file.write(f"sentence {i} - {tag2}: {line2}\n")

# Example usage:
# Adjust 'input.txt' to the path of your input file, 'output.txt' to your desired output file name
# and ('text1', 'text2', 4) to your specific arguments
format_text_lines_to_file('dictionary/mlm_training_dataset.txt', 'Maranao', 'English', 5549, 'dictionary/mlm_training_dataset_formatted.txt')


