import functools
import sacrebleu
import re
from collections import Counter

def index_to_column(index):
    column = ""
    while index >= 0:
        index, remainder = divmod(index, 26)
        column = chr(65 + remainder) + column
        index -= 1
    return column

class Samples:
    def __init__(self):
        self.samples = []
        self.votes = []
        self.num_top_bleu = 3

    def add_sample(self, sample):
        self.samples.append(sample)

    @property
    @functools.lru_cache()
    def top_bleu_samples(self):
        # Calculate BLEU scores for each sentence against all others
        self.method = 'top_bleu'
        bleu_scores = {}
        for i, candidate in enumerate(self.samples):
            references = [ref for j, ref in enumerate(self.samples) if i != j]
            score = sacrebleu.sentence_bleu(candidate, references).score
            bleu_scores[self.samples[i]] = score

        # Sort sentences by their BLEU score in descending order
        sorted_sentences = sorted(bleu_scores, key=bleu_scores.get, reverse=True)

        sorted_sentences = [f'[{index_to_column(i)}] {sentence}' for i, sentence in enumerate(sorted_sentences)]

        # Return the top n distinct sentences with the highest scores
        return sorted_sentences[:self.num_top_bleu]
    

    @property
    @functools.lru_cache()
    def all_samples(self):
        self.method = 'all'
        return [f'[{index_to_column(i)}] {sentence}' for i, sentence in enumerate(self.samples)]


    def submit_vote(self, vote_str):
        # Get the last letter in square brackets
        # vote_letter = [match for match in re.findall(r'\[(.*?)\]', vote_str)][-1].upper()
        vote_letter = re.sub(r'[^A-Z]', '', [match for match in re.findall(r'\[(.*?)\]', vote_str)][-1]).upper()
        print(f'Vote submitted: {vote_letter}')
        self.votes.append(vote_letter)


    @property
    def majority_vote(self):
        winner_letter, _ = Counter(self.votes).most_common(1)[0]
        # Determine if the vote was cast based on a selection of all sentences or just the top bleu-scored sentences
        sentences = self.all_samples if self.method == 'all' else self.top_bleu_samples
        # Obtain the sentence corresponding to the winning vote
        winner = next((s[len(winner_letter)+3:] for s in sentences if s.startswith(f'[{winner_letter}] ')), 'Sentence not found')
        return winner