import os
import tempfile
from typing import List, Callable
import tiktoken

def count_tokens(string: str) -> int:
    """Returns the number of tokens in a text string using tiktoken's specified encoding."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens

class TextFileProcessor:
    def __init__(self, file_paths: List[str], text_split_function: Callable):
        self.file_paths = file_paths
        self.text_split = text_split_function
        self.temp_directory = tempfile.mkdtemp(dir=tempfile.gettempdir())
        self.temp_files = []
        self.max_chunks_per_file = 2000 # 2048
        self.max_tokens_per_file = 900000 # 1000000
        self.max_tokens_per_chunk = 8000 # 8191

        self.process_files()

    def write_temp_file(self, chunks):
        """ Write chunks to a temporary file in the designated temp directory. """
        with tempfile.NamedTemporaryFile(delete=False, mode='w', dir=self.temp_directory, suffix='.txt', encoding='utf-8') as temp_file:
            token_counts = [count_tokens(chunk) for chunk in chunks]
            max_tokens_in_chunk = max(token_counts)
            total_tokens = sum(token_counts)
            print(f"Writing {len(chunks)} chunks to {temp_file.name}")
            print(f"Largest chunk size: {max_tokens_in_chunk} tokens")
            print(f"Total tokens being written: {total_tokens}")
            for chunk in chunks:
                temp_file.write(chunk + '\n')
            self.temp_files.append(temp_file.name)
            print(f'File location: {temp_file.name}')
            return temp_file.name

    def process_files(self):
        """ Process each file, splitting the text and managing token constraints. """
        for file_path in self.file_paths:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

            chunks = self.text_split(text)
            temp_file_chunks = []
            current_token_count = 0

            for chunk in chunks:
                chunk_token_count = count_tokens(chunk)
                
                if chunk_token_count > self.max_tokens_per_chunk:
                    # Break the chunk into smaller pieces if exceeding max tokens per chunk
                    small_chunks = self.break_chunk(chunk)
                    for small_chunk in small_chunks:
                        small_chunk_token_count = count_tokens(small_chunk)
                        if len(temp_file_chunks) >= self.max_chunks_per_file or \
                           current_token_count + small_chunk_token_count > self.max_tokens_per_file:
                            self.write_temp_file(temp_file_chunks)
                            temp_file_chunks = [small_chunk]
                            current_token_count = small_chunk_token_count
                        else:
                            temp_file_chunks.append(small_chunk)
                            current_token_count += small_chunk_token_count
                else:
                    if len(temp_file_chunks) >= self.max_chunks_per_file or \
                       current_token_count + chunk_token_count > self.max_tokens_per_file:
                        self.write_temp_file(temp_file_chunks)
                        temp_file_chunks = [chunk]
                        current_token_count = chunk_token_count
                    else:
                        temp_file_chunks.append(chunk)
                        current_token_count += chunk_token_count

            # Handle any remaining chunks
            if temp_file_chunks:
                self.write_temp_file(temp_file_chunks)

    def break_chunk(self, chunk: str) -> List[str]:
        """ Breaks a large chunk into smaller chunks that conform to token limits. """
        # Simplified breaking method; implement a more sophisticated breaking logic as needed
        words = chunk.split()
        small_chunks = []
        current_chunk = []
        current_count = 0

        for word in words:
            word_token_count = count_tokens(word)
            if current_count + word_token_count > self.max_tokens_per_chunk:
                small_chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_count = word_token_count
            else:
                current_chunk.append(word)
                current_count += word_token_count
        
        if current_chunk:
            small_chunks.append(' '.join(current_chunk))
        return small_chunks

# # Example usage:
# # Define the text splitting function externally
# def external_text_split_function(text: str) -> List[str]:
#     # Implementation of text splitting here
#     return text.split('\n')  # Simplified example; replace with actual text splitting logic

# # Instantiate the class with file paths and the text splitting function
# processor = TextFileProcessor(['path/to/your/file1.txt', 'path/to/your/file2.txt'], external_text_split_function)
# processor.process_files()
