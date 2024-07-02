import os

def count_token(text):
    # Simplistic token counting: split by whitespace. Adjust as necessary.
    return len(text.split())

def split_text_to_chunks(text, max_tokens=4000, must_break_at_empty_line=True):
    print(f"Starting split with max_tokens={max_tokens}, must_break_at_empty_line={must_break_at_empty_line}")
    chunks = []
    lines = text.split("\n")
    lines_tokens = [count_token(line) for line in lines]
    sum_tokens = sum(lines_tokens)
    print(f"Total tokens in document: {sum_tokens}")

    while sum_tokens > max_tokens:
        print("Current sum_tokens exceeds max_tokens, attempting to split...")
        estimated_line_cut = int(max_tokens / sum_tokens * len(lines)) + 1
        cnt = 0
        prev = ""
        for cnt in reversed(range(estimated_line_cut)):
            if must_break_at_empty_line and lines[cnt].strip() != "":
                continue
            if sum(lines_tokens[:cnt]) <= max_tokens:
                prev = "\n".join(lines[:cnt])
                break
        if cnt == 0:
            print(f"max_tokens too small to fit a single line. First line: {lines[0][:100]}")
            if not must_break_at_empty_line:
                split_len = int(max_tokens / lines_tokens[0] * 0.9 * len(lines[0]))
                prev = lines[0][:split_len]
                lines[0] = lines[0][split_len:]
                lines_tokens[0] = count_token(lines[0])
            else:
                print("Failed to split docs with must_break_at_empty_line being True. Consider setting to False.")
                break
        if prev:
            chunks.append(prev)
        lines = lines[cnt:]
        lines_tokens = lines_tokens[cnt:]
        sum_tokens = sum(lines_tokens)
        print(f"Created a chunk, remaining tokens: {sum_tokens}")

    if lines:
        text_to_chunk = "\n".join(lines)
        if len(text_to_chunk) > 10:  # Ensuring chunk is significant
            chunks.append(text_to_chunk)

    return chunks

# Example usage:
text_file_path = "dictionary/english-maranao.txt"  # Update this to your file path
max_tokens = 2000  # Adjust based on your requirements

with open(text_file_path, 'r', encoding='utf-8') as file:
    text_content = file.read()

chunks = split_text_to_chunks(text_content, max_tokens=max_tokens, must_break_at_empty_line=True)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}:")
    print(chunk[:500], "...")  # Print first 500 characters of each chunk to avoid flooding the output
