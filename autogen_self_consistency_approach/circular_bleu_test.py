import nltk
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize
from nltk.util import ngrams

# Ensure that the necessary NLTK components are downloaded
nltk.download('punkt')

def boundary_extended_ngrams(sentence_tokens, n):
    """Extend sentence by repeating the first n-1 words at the end for n-gram continuity."""
    if n == 1:
        return sentence_tokens  # No extension needed for unigrams
    tokens = sentence_tokens + sentence_tokens[:n-1]  # Extend tokens by repeating the start
    return list(ngrams(tokens, n))

def modified_sentence_bleu(reference_sentences, candidate_sentence, max_ngram_order):
    """Calculate the BLEU score with modified boundary n-grams."""
    tokenized_candidate = word_tokenize(candidate_sentence)
    tokenized_references = [word_tokenize(ref) for ref in reference_sentences]
    
    # Prepare weights based on the maximum n-gram order
    weights = tuple(1.0 / max_ngram_order for _ in range(max_ngram_order))

    # Calculate BLEU using modified n-grams
    smoothing = nltk.translate.bleu_score.SmoothingFunction().method1
    bleu_score = sentence_bleu(
        [boundary_extended_ngrams(ref, max_ngram_order) for ref in tokenized_references],
        boundary_extended_ngrams(tokenized_candidate, max_ngram_order),
        weights=weights,
        smoothing_function=smoothing
    )
    return bleu_score

# Example sentences with one word changed in each
sentences = [
    "A quick brown fox jumps over the lazy dog.",
    "The slick brown fox jumps over the lazy dog.",
    "The quick red fox jumps over the lazy dog.",
    "The quick brown cow jumps over the lazy dog.",
    "The quick brown fox leaps over the lazy dog.",
    "The quick brown fox jumps above the lazy dog.",
    "The quick brown fox jumps over a lazy dog.",
    "The quick brown fox jumps over the sleeping dog.",
    "The quick brown fox jumps over the lazy cat."
]

# Calculate and print the modified BLEU scores with boundary extensions
max_ngram_order = 4  # Example using up to 4-grams
for sentence in sentences:
    print(f"Sentence: '{sentence}'")
    score = modified_sentence_bleu(sentences, sentence, max_ngram_order)
    print("Modified BLEU Score with Boundary Extension:", score)
    print()
