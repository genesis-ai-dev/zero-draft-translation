from sacrebleu.metrics import BLEU, CHRF
import json
from datetime import datetime
import os
import re
import unicodedata
from Levenshtein import distance as levenshtein_distance
from collections import namedtuple

class ScoreContainer:
    def __init__(self, individual, overall):
        self.individual = individual
        self.overall = overall

class TranslationMetric:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.generated = None
        self.reference = None
        self.scores = {}
        self.metrics = {
            "characTER": self._character_score,
            "chrF": self._chrf_score,
            "BLEU": self._bleu_score
        }

    def _character_score(self, gen, ref):
        gen_chars = self._preprocess(gen)
        ref_chars = self._preprocess(ref)
        edit_distance = levenshtein_distance(gen_chars, ref_chars)
        return edit_distance / max(len(gen_chars), len(ref_chars))

    def _preprocess(self, text):
        # Remove whitespace and punctuation
        return ''.join(ch for ch in text if not unicodedata.category(ch).startswith('P') and not ch.isspace())

    def _chrf_score(self, gen, ref):
        chrf = CHRF()
        return chrf.corpus_score([gen], [[ref]]).score

    def _bleu_score(self, gen, ref):
        bleu = BLEU()
        return bleu.corpus_score([gen], [[ref]]).score

    def _load_text(self, input_text):
        if isinstance(input_text, list):
            return input_text
        elif os.path.isfile(input_text):
            with open(input_text, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file if line.strip()]
        else:
            return [line.strip() for line in input_text.split('\n') if line.strip()]

    def compare_translations(self, generated, reference):
        self.generated = self._load_text(generated)
        self.reference = self._load_text(reference)

        if len(self.generated) != len(self.reference):
            raise ValueError("Generated and reference translations have different number of lines.")

        for metric_name, metric_func in self.metrics.items():
            individual_scores = [metric_func(gen, ref) for gen, ref in zip(self.generated, self.reference)]
            overall_score = sum(individual_scores) / len(individual_scores)
            self.scores[metric_name] = ScoreContainer(individual_scores, overall_score)

        return self.scores

    def generate_report(self, file_path):
        if not self.scores:
            raise ValueError("No scores available. Run compare_translations first.")
        
        report = {
            "datetime": datetime.now().isoformat(),
            "generated_translation": self.generated,
            "reference_translation": self.reference,
            "scores": {
                metric: {
                    "overall": score.overall,
                    "individual": score.individual
                } for metric, score in self.scores.items()
            },
            "parameters": self.kwargs
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

        print(f"Report generated and saved to {file_path}")

# Example usage
# evaluator = TranslationEvaluator(model_name="MyTranslationModel", version="1.0")

# generated_translation = """This is a generated translation.
# This is the second line.
# And here's a third line."""

# gold_standard = """This is the gold standard translation.
# This is also the second line.
# And the third line is here."""

# results = evaluator.compare_translations(generated_translation, gold_standard)

# # Accessing overall scores
# for metric, score in results.items():
#     print(f"{metric} overall score: {score.overall}")

# # Accessing individual scores
# print("\nIndividual scores for characTER:")
# for i, score in enumerate(results['characTER'].individual):
#     print(f"Line {i+1}: {score}")

# # Accessing a specific individual score
# print(f"\ncharacTER score for line 2: {results['characTER'].individual[1]}")

# evaluator.generate_report("translation_evaluation_report.json")