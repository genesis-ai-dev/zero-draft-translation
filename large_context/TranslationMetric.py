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
        self.generated = []
        self.reference = []
        self.vrefs = []
        self.ngram_scores = []
        self.scores = {}
        self.metrics = {
            "characTER": self._character_score,
            "chrF": self._chrf_score,
            "BLEU": self._bleu_score
        }
        self.report_path = None

    def _character_score(self, gen, ref):
        gen_chars = self._preprocess(gen)
        ref_chars = self._preprocess(ref)
        edit_distance = levenshtein_distance(gen_chars, ref_chars)
        return edit_distance / max(len(gen_chars), len(ref_chars))

    def _preprocess(self, text):
        return ''.join(ch for ch in text if not unicodedata.category(ch).startswith('P') and not ch.isspace())

    def _chrf_score(self, gen, ref):
        chrf = CHRF()
        return chrf.corpus_score([gen], [[ref]]).score

    def _bleu_score(self, gen, ref):
        bleu = BLEU()
        return bleu.corpus_score([gen], [[ref]]).score

    def _load_text(self, input_text):
        input_text = [line.replace('\u202B', '').replace('\u202C', '') for line in input_text]
        
        if isinstance(input_text, list):
            return input_text
        elif os.path.isfile(input_text):
            with open(input_text, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file if line.strip()]
        else:
            return [line.strip() for line in input_text.split('\n') if line.strip()]

    def initialize_report(self, file_path):
        self.report_path = file_path
        report = {
            "datetime": datetime.now().isoformat(),
            "generated_translation": [],
            "reference_translation": [],
            "ngram_scores": [],
            "scores": {metric: {"overall": 0, "individual": []} for metric in self.metrics},
            "parameters": self.kwargs
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

    def update_report(self, verse, generated, reference, vref, ngram_score):
        self.generated.append(generated)
        self.reference.append(reference)
        self.vrefs.append(vref)
        self.ngram_scores.append(ngram_score)

        with open(self.report_path, 'r+', encoding='utf-8') as f:
            report = json.load(f)
            report["generated_translation"].append(f"{vref} {generated}")
            report["reference_translation"].append(f"{vref} {reference}")
            report["ngram_scores"].append(ngram_score)
            
            for metric_name, metric_func in self.metrics.items():
                score = metric_func(generated, reference)
                report["scores"][metric_name]["individual"].append(score)
                overall = sum(report["scores"][metric_name]["individual"]) / len(report["scores"][metric_name]["individual"])
                report["scores"][metric_name]["overall"] = overall

            f.seek(0)
            json.dump(report, f, indent=4, ensure_ascii=False)
            f.truncate()

    def finalize_report(self):
        with open(self.report_path, 'r+', encoding='utf-8') as f:
            report = json.load(f)
            report["datetime_finished"] = datetime.now().isoformat()
            f.seek(0)
            json.dump(report, f, indent=4, ensure_ascii=False)
            f.truncate()

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