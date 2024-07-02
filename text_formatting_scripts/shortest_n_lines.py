import sys

def find_shortest_lines(filename: str, n: int) -> None:
    """
    Reads a text file and prints the shortest `n` lines.
    
    :param filename: Path to the text file.
    :param n: Number of shortest lines to find and print.
    """
    try:
        # Read lines from the file
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Remove leading/trailing whitespace and sort lines by length
        lines = [line.strip() for line in lines if line.strip()]
        sorted_lines = sorted(lines, key=len)

        # Get the shortest `n` lines
        shortest_lines = sorted_lines[:n]

        # Print the shortest lines
        for line in shortest_lines:
            print(line)

    except FileNotFoundError:
        print("Error: The file does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


find_shortest_lines('dictionary/quran_english_target.txt', 5)
