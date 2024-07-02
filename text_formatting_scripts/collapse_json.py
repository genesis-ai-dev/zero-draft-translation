import json

def collapse_json_to_text(json_file_path: str, output_file_path: str):
    """
    Reads a JSON file, collapses each dictionary entry into a single line, 
    and writes them to a text file.

    :param json_file_path: Path to the input JSON file.
    :param output_file_path: Path to the output text file where the collapsed lines will be saved.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file, \
             open(output_file_path, 'w', encoding='utf-8') as text_file:
            # Load the JSON data from file
            data = json.load(json_file)

            # Ensure the data is a list of dictionaries
            if not isinstance(data, list):
                raise ValueError("The JSON file must contain a list of dictionaries.")

            # Process each dictionary in the list
            for entry in data:
                # Convert dictionary to a single-line JSON string
                json_string = json.dumps(entry, separators=(',', ':'))
                # Write the single-line JSON string to the text file
                text_file.write(json_string + '\n')

    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' does not exist.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON. Check if the file contains valid JSON.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
collapse_json_to_text('dictionary/target_dictionary.json', 'dictionary/target_dictionary.txt')
