from gensim.models.fasttext import FastText as FT_gensim
from gensim.models import KeyedVectors
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer, util

class SimilarityScorer:
    def __init__(self, model_path):
        self.w2v_weight = 0.0
        self.st_weight = 0.7
        self.struct_diversity_weight = 0.3
        self.length_similarity_weight = 0.0

        # Load a pre-trained FastText model (Wikipedia English)
        # self.model = FT_gensim.load(model_path)
        if self.w2v_weight > 0:    
            print("Loading model...")
            self.model = KeyedVectors.load_word2vec_format(model_path, binary=False)
            print("Model loaded.")

        # Initialize the Sentence Transformer model
        self.sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')

    def calculate_semantic_similarity(self, text1, text2):
        # Split the texts into words
        words1 = text1.lower().split()
        words2 = text2.lower().split()

        # Calculate semantic similarity using the model
        # FastText can handle out-of-vocabulary words, so no need to filter
        # similarity = self.model.wv.n_similarity(words1, words2)

        # Calculate semantic similarity using the model
        # Ensure that words are in the model's vocabulary
        words1 = [word for word in words1 if word in self.model.key_to_index]
        words2 = [word for word in words2 if word in self.model.key_to_index]

        if not words1 or not words2:
            # If either sentence has no words that are in the vocabulary, return 0 similarity
            return 0
        similarity = self.model.n_similarity(words1, words2)

        return similarity

    def calculate_semantic_similarity_sentence_transformers(self, text1, text2):
        # Encode the texts to get their embeddings
        embeddings1 = self.sentence_model.encode([text1])[0]
        embeddings2 = self.sentence_model.encode([text2])[0]

        # Compute cosine similarity between the embeddings
        cosine_sim = util.pytorch_cos_sim(embeddings1, embeddings2)

        return cosine_sim.item()
    
    def calculate_structural_diversity(self, text1, text2):
        # Use FuzzyWuzzy to calculate the similarity (returning 100 for identical strings)
        return fuzz.ratio(text1, text2)

    def score_prediction(self, example, prediction, trace=None):
        print("Scoring prediction...")
        
        # Calculate average length of the example verses
        example_lengths = [len(example.verse_ver_1), len(example.verse_ver_2), len(example.verse_ver_3)]
        avg_example_length = sum(example_lengths) / len(example_lengths)
        
        # Calculate length of the predicted verse
        predicted_length = len(prediction.mixed_verse)
        
        # Calculate length similarity
        length_similarity_score = 1 - (abs(predicted_length - avg_example_length) / avg_example_length)
        length_similarity_score = max(length_similarity_score, 0)
        
        # Compare prediction to each verse version for semantic similarity using Word2Vec
        if self.w2v_weight > 0:
            semantic_similarities_w2v = [
                self.calculate_semantic_similarity(example.verse_ver_1, prediction.mixed_verse),
                self.calculate_semantic_similarity(example.verse_ver_2, prediction.mixed_verse),
                self.calculate_semantic_similarity(example.verse_ver_3, prediction.mixed_verse)
            ]
            avg_semantic_similarity_w2v = sum(semantic_similarities_w2v) / len(semantic_similarities_w2v)
        else:
            avg_semantic_similarity_w2v = 0

        # Compare prediction to each verse version for semantic similarity using Sentence Transformers
        if self.st_weight > 0:
            semantic_similarities_st = [
                self.calculate_semantic_similarity_sentence_transformers(example.verse_ver_1, prediction.mixed_verse),
                self.calculate_semantic_similarity_sentence_transformers(example.verse_ver_2, prediction.mixed_verse),
                self.calculate_semantic_similarity_sentence_transformers(example.verse_ver_3, prediction.mixed_verse)
            ]
            avg_semantic_similarity_st = sum(semantic_similarities_st) / len(semantic_similarities_st)
        else:
            avg_semantic_similarity_st = 0
        
        # Calculate structural diversity
        structural_diversities = [
            100 - self.calculate_structural_diversity(example.verse_ver_1, prediction.mixed_verse),
            100 - self.calculate_structural_diversity(example.verse_ver_2, prediction.mixed_verse),
            100 - self.calculate_structural_diversity(example.verse_ver_3, prediction.mixed_verse)
        ]
        
        # Average the similarities and diversities
        avg_structural_diversity = sum(structural_diversities) / len(structural_diversities)

        normalized_structural_diversity = avg_structural_diversity / 100

        desired_structural_diversity = 0.2

        struct_diversity_score = -4 * (normalized_structural_diversity - desired_structural_diversity) ** 2 + 1.0
        struct_diversity_score = max(struct_diversity_score, 0)

        # Integrate the sentence transformer similarity into the final score
        final_score = (avg_semantic_similarity_w2v * self.w2v_weight) + (avg_semantic_similarity_st * self.st_weight) + (struct_diversity_score * self.struct_diversity_weight) + (length_similarity_score * self.length_similarity_weight)
        
        print(f"Predicted verse: {prediction.mixed_verse}")
        print("Average semantic similarity (Word2Vec):", avg_semantic_similarity_w2v)
        print("Average semantic similarity (Sentence Transformers):", avg_semantic_similarity_st)
        print("Normalized structural diversity:", normalized_structural_diversity)
        print("Structural diversity score:", struct_diversity_score)
        print("Length similarity score:", length_similarity_score)
        print("Final score:", final_score)

        return final_score

