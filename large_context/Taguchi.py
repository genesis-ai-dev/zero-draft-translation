import numpy as np
from itertools import combinations
from typing import Dict, List, Any
from scipy import stats
from scipy.stats import chi2_contingency

class TaguchiOptimizer:
    def __init__(self, factors: Dict[str, List[Any]], strength: int = 2):
        self.factors = factors
        self.strength = strength
        self.array = None
        self.results = None
        self.factor_effects = None

    def create_taguchi_array(self):
        num_factors = len(self.factors)
        factor_levels = [len(levels) for levels in self.factors.values()]
        
        # Determine the size of the array
        array_size = self.calculate_array_size(factor_levels)
        
        # Generate the array using Bose-Bush method
        self.array = self.bose_bush_algorithm(array_size, factor_levels)
        
        # Check orthogonality and balance
        if not self.check_orthogonality_and_balance():
            raise ValueError("Generated array is not orthogonal or balanced")

        # Map the array to factor names
        factor_names = list(self.factors.keys())
        self.array = [{factor_names[i]: row[i] for i in range(num_factors)} for row in self.array]

    def calculate_array_size(self, factor_levels):
        max_level = max(factor_levels)
        return max(max_level ** self.strength, max_level * (max_level - 1) + 1)

    def bose_bush_algorithm(self, size, factor_levels):
        num_factors = len(factor_levels)
        array = np.zeros((size, num_factors), dtype=int)
        
        # Generate first two columns
        for i in range(size):
            array[i, 0] = i % factor_levels[0]
            array[i, 1] = (i // factor_levels[0]) % factor_levels[1]
        
        # Generate remaining columns
        for j in range(2, num_factors):
            for i in range(size):
                array[i, j] = (array[i, 0] + j * array[i, 1]) % factor_levels[j]
        
        # Add 1 to all elements (Taguchi arrays typically use 1-based indexing)
        return array + 1

    def check_orthogonality_and_balance(self):
        num_factors = len(self.factors)
        
        # Check balance
        for col in range(num_factors):
            levels, counts = np.unique(self.array[:, col], return_counts=True)
            if not np.all(counts == counts[0]):
                return False
        
        # Check orthogonality
        for combo in combinations(range(num_factors), self.strength):
            contingency_table = self.create_contingency_table(combo)
            _, p_value, _, _ = chi2_contingency(contingency_table)
            if p_value < 0.05:  # Using 0.05 as the significance level
                return False
        
        return True

    def create_contingency_table(self, columns):
        levels = [len(self.factors[list(self.factors.keys())[col]]) for col in columns]
        table = np.zeros(levels, dtype=int)
        for row in self.array:
            index = tuple(row[col] - 1 for col in columns)
            table[index] += 1
        return table

    def run_experiments(self):
        self.results = []
        for experiment in self.array:
            result = self.run_test(**experiment)
            self.results.append(result)

    def run_test(self, **kwargs):
        # This is a placeholder method. In reality, this would run your actual experiment.
        # For demonstration, we'll just return a random score.
        return np.random.rand()

    def analyze_results(self, metric: str):
        num_factors = len(self.factors)
        num_experiments = len(self.results)

        self.factor_effects = {}
        for i, factor in enumerate(self.factors.keys()):
            factor_levels = set(exp[factor] for exp in self.array)
            level_means = []
            for level in factor_levels:
                level_results = [self.results[j] for j in range(num_experiments) if self.array[j][factor] == level]
                level_means.append(np.mean(level_results))
            
            f_statistic, p_value = stats.f_oneway(*[
                [self.results[j] for j in range(num_experiments) if self.array[j][factor] == level]
                for level in factor_levels
            ])
            
            self.factor_effects[factor] = {
                'level_means': level_means,
                'f_statistic': f_statistic,
                'p_value': p_value
            }

    def get_optimal_settings(self, fixed_factors: Dict[str, Any], metric: str) -> Dict[str, Any]:
        if self.factor_effects is None:
            self.analyze_results(metric)

        optimal_settings = fixed_factors.copy()
        for factor, levels in self.factors.items():
            if factor not in fixed_factors:
                optimal_level = self.determine_best_level(factor, metric)
                optimal_settings[factor] = levels[optimal_level]
        return optimal_settings

    def determine_best_level(self, factor: str, metric: str) -> int:
        level_means = self.factor_effects[factor]['level_means']
        return np.argmax(level_means)

    def map_experiment_to_settings(self, experiment: tuple) -> Dict[str, Any]:
        return {factor: levels[exp] for (factor, levels), exp in zip(self.factors.items(), experiment)}

# Usage example
factors = {
    'model': ['Sonnet 3.5', 'Opus', 'Haiku'],
    'num_examples': [8, 32, 128],
    'n_gram': [2, 3, 4],
    'genre': ['Gospel', 'Apocalyptic', 'Prophetic', 'Law'],
    'source_language': ['English', 'Arabic'],
    'target_language': ['Tamazight', 'Zanskari'],
}

optimizer = TaguchiOptimizer(factors)
optimizer.create_taguchi_array()
optimizer.run_experiments()

fixed_factors = {
    'source_language': 'English',
    'target_language': 'Tamazight',
    'genre': 'Apocalyptic'
}

optimal_settings = optimizer.get_optimal_settings(fixed_factors, metric='BLEU')
print("Optimal settings:", optimal_settings)

# Print factor effects
print("\nFactor Effects:")
for factor, effect in optimizer.factor_effects.items():
    print(f"{factor}:")
    print(f"  Level means: {effect['level_means']}")
    print(f"  F-statistic: {effect['f_statistic']}")
    print(f"  p-value: {effect['p_value']}")