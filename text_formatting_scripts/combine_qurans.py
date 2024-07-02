def combine_files(file1, file2, output_file, keyword1, keyword2):
    with open(file1, 'r', encoding='utf-8') as f1, \
         open(file2, 'r', encoding='utf-8') as f2, \
         open(output_file, 'w', encoding='utf-8') as outfile:

        # Iterate over the lines of both files simultaneously
        for line1, line2 in zip(f1, f2):
            # Strip newline characters from the end of lines if present
            line1 = line1.rstrip()
            line2 = line2.rstrip()
            
            # Extract the sequence number from the first file's line
            sequence_number = line1.split(' ')[0]
            
            # Write the formatted lines with keywords to the output file
            outfile.write(f"{sequence_number} ({keyword1}) {line1[len(sequence_number)+1:]}\n")
            outfile.write(f"{sequence_number} ({keyword2}) {line2[len(sequence_number)+1:]}\n")

# Example usage
file1 = 'dictionary/quran_english_formatted_2.txt'  # Replace with your first file's name
file2 = 'dictionary/quran_maranao_formatted_2.txt'  # Replace with your second file's name
output_file = 'dictionary/quran_english_maranao.txt'  # Replace with your desired output file's name
keyword1 = 'English'  # Replace with your first keyword
keyword2 = 'Maranao'  # Replace with your second keyword

combine_files(file1, file2, output_file, keyword1, keyword2)
