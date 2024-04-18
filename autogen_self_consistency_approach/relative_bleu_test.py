import sacrebleu
from nltk.tokenize import word_tokenize

# Prepare a list of 20 variations of a sentence.
translations = [
    "A quick brown fox jumps over the lazy dog.",
    "The slick brown fox jumps over the lazy dog.",
    "The quick red fox jumps over the lazy dog.",
    "The quick brown cow jumps over the lazy dog.",
    "The quick brown fox leaps over the lazy dog.",
    "The quick brown fox jumps above the lazy dog.",
    "The quick brown fox jumps over a lazy dog.",
    "The quick brown fox jumps over the sleeping dog.",
    "The quick brown fox jumps over the lazy cat.",
]

# Tokenize all translations
tokenized_translations = [word_tokenize(t) for t in translations]

# Calculate BLEU scores for each translation against all others
bleu_scores = {}
for i, candidate in enumerate(tokenized_translations):
    references = [ref for j, ref in enumerate(tokenized_translations) if i != j]
    # Join tokens back to sentences for sacrebleu
    candidate_sentence = ' '.join(candidate)
    reference_sentences = [' '.join(ref) for ref in references]
    score = sacrebleu.sentence_bleu(candidate_sentence, reference_sentences).score
    bleu_scores[translations[i]] = score
    print(f"Translation: '{translations[i]}'\nScore: {score}\n")

# Determine the translation with the highest BLEU score
best_translation = max(bleu_scores, key=bleu_scores.get)
best_score = bleu_scores[best_translation]

print(f"The most consistent translation based on relative sentence BLEU scores is: '{best_translation}' with a BLEU score of: {best_score}")