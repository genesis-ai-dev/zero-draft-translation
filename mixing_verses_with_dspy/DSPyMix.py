import dspy
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate
import openai
from fuzzywuzzy import fuzz
import numpy as np
from dotenv import load_dotenv
import os
from VerseMetric import SimilarityScorer

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

openai.api_base = 'http://localhost:1234/v1'
openai.api_key = ''

local_llm = dspy.OpenAI()

gpt3 = dspy.OpenAI(model='gpt-3.5-turbo', max_tokens=250, api_key=api_key)

gpt4 = dspy.OpenAI(model='gpt-4', max_tokens=250, api_key=api_key)

# Set model here
dspy.settings.configure(lm=local_llm)


class Pirate(dspy.Signature):
    """Translate the input Bible verse into Pirate speak."""
    verse = dspy.InputField()
    pirate_verse = dspy.OutputField()

class MixTranslations(dspy.Signature):
    """Produce a fourth version based on three input versions. Gives only the fourth version, nothing else."""
    verse_ver_1 = dspy.InputField()
    verse_ver_2 = dspy.InputField()
    verse_ver_3 = dspy.InputField()
    mixed_verse = dspy.OutputField()

# class RemoveCommentary(dspy.Signature):
#     """Only provide the new verse. Remove everything else."""
#     verse = dspy.InputField()
#     mixed_verse = dspy.OutputField()

class Mod(dspy.Module):
    def __init__(self):
        super().__init__()
        
        self.translate = dspy.ChainOfThought(MixTranslations)
        # self.clean = dspy.ChainOfThought(RemoveCommentary)

    def forward(self, verse_ver_1, verse_ver_2, verse_ver_3):
        new_verse = self.translate(verse_ver_1=verse_ver_1, verse_ver_2=verse_ver_2, verse_ver_3=verse_ver_3) # temperature=0.2 # .mixed_1_verse
        # new_verse = self.clean(verse=new_verse)
        return new_verse
    
    # def forward(self, verse):
    #     return self.translate(verse=verse, temperature=0.2)
    
class Mix():
    def __init__(self, compile=False):
        self.module = Mod()
        self.compiled_state_filepath = 'compiled_states/compiled_state_mix.json'

        examples = [
            dspy.Example(
                verse_ver_1='In the beginning God created the heaven and the earth.', 
                verse_ver_2='First this: God created the Heavens and Earth', 
                verse_ver_3='In the beginning God created the sky and the earth.',
                # output_verse='At the start, God formed the heavens and the earth.'
                ),
            dspy.Example(
                verse_ver_1='Then I bathed you with water, washed all the blood off of you, and put oil on you.', 
                verse_ver_2='Then washed I thee with water; yea, I throughly washed away thy blood from thee, and I anointed thee with oil.',
                verse_ver_3='Then I washed you with water, thoroughly washed off your blood, and anointed you with oil.',
                # output_verse='I then cleansed you with water, removing all blood, and gently applied oil.'
                ),
            dspy.Example(
                verse_ver_1='Whoso loveth instruction loveth knowledge: but he that hateth reproof is brutish.',
                verse_ver_2='Whoever loves instruction loves knowledge, but he who hates correction is stupid.',
                verse_ver_3='To learn, you must want to be taught. To refuse reproof is stupid.',
                # output_verse='Loving to learn is to embrace knowledge, while spurning correction is folly.'
                ),
            dspy.Example(
                verse_ver_1='Even when walking through the dark valley of death I will not be afraid, for you are close beside me, guarding, guiding all the way.',
                verse_ver_2='Even though I walk through the valley of the shadow of death, I will fear no evil, for you are with me; your rod and your staff, they comfort me.',
                verse_ver_3='Yea, though I walk through the valley of the shadow of death, I will fear no evil: for thou art with me; thy rod and thy staff they comfort me.',
                # output_verse='Walking through death\'s shadowed vale, I fear nothing, for you shield and guide me.'
                ),
            dspy.Example(
                verse_ver_1='Mine heritage is unto me as a lion in the forest; it crieth out against me: therefore have I hated it.',
                verse_ver_2='My heritage is to Me as a lion in the forest. She cries out against Me; therefore I have hated her.',
                verse_ver_3='My inheritance has become to Me Like a lion in the forest; She has [e]roared against Me; Therefore I have come to hate her.',
                # output_verse='My legacy roars at me like a forest lion, provoking my disdain.'
                ),
            dspy.Example(
                verse_ver_1='For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.',
                verse_ver_2='For this is how God loved the world: He gave his one and only Son, so that everyone who believes in him will not perish but have eternal life.',
                verse_ver_3='For God loved the world in this way: He gave his only Son, so that everyone who believes in him will not perish but have eternal life.',
                # output_verse='God''s love for the world was shown by giving His only Son, ensuring believers would gain everlasting life.'
                ),
            dspy.Example(
                verse_ver_1='I can do all things through Christ who strengthens me.',
                verse_ver_2='I am able to do all things through Him who strengthens me.',
                verse_ver_3='I have the strength for everything through him who empowers me.',
                # output_verse='Through Christ\'s strength, all becomes possible for me.'
                ),
            dspy.Example(
                verse_ver_1='Trust in the Lord with all your heart and lean not on your own understanding;',
                verse_ver_2='Trust in the Lord with all your heart; do not depend on your own understanding.',
                verse_ver_3='Trust in the Lord with all your heart, and do not rely on your own insight.',
                # output_verse='With all your heart, trust in the Lord, and forsake reliance on personal insight.'
                ),
            dspy.Example(
                verse_ver_1='The Lord is my shepherd, I lack nothing.',
                verse_ver_2='The Lord is my shepherd; I shall not want.',
                verse_ver_3='The Lord is my shepherd, I shall not be in want.',
                # output_verse='Under the Lord\'s shepherding, I am in want of nothing.'
                ),
            dspy.Example(
                verse_ver_1='For the wages of sin is death, but the gift of God is eternal life in Christ Jesus our Lord.',
                verse_ver_2='For the payoff of sin is death, but the gift of God is eternal life in Christ Jesus our Lord.',
                verse_ver_3='For the wages of sin is death; but the gift of God is eternal life through Jesus Christ our Lord.',
                # output_verse='Sin\'s reward is death, yet God offers eternal life through His Son, Christ Jesus.'
            )
            ]

        self.examples = [x.with_inputs('verse_ver_1', 'verse_ver_2', 'verse_ver_3') for x in examples]
        


        if compile:
            self.compile()
        else:
            self.load()
    
    def mix_metric(self, example, prediction, trace=None):
        verses = [example.verse_ver_1, example.verse_ver_2, example.verse_ver_3]
        # Similarity scoring
        similarities = [fuzz.token_set_ratio(prediction.mixed_verse, input_verse) for input_verse in verses]
        avg_similarity = np.mean(similarities)
        
        # Ensure we're rewarding lower similarity for variation
        variation_score = 100 - avg_similarity
        
        # Length evaluation
        avg_length = np.mean([len(input_verse) for input_verse in verses])
        length_difference = abs(len(prediction.mixed_verse) - avg_length)
        
        # Normalize length difference to a score
        # Assuming a maximum expected difference, adjust based on your data
        max_expected_diff = 50
        length_score = max(0, 100 - (length_difference / max_expected_diff) * 100)
        
        # Combine scores
        # Adjust weighting if necessary
        final_score = (variation_score + length_score) / 2 / 100
        print(f'**Predicted verse: {prediction.mixed_verse}')
        print(f"**Final score: {final_score}")
        return final_score



    def compile(self):
        compiled_state_filepath = self.compiled_state_filepath
        config = dict(max_bootstrapped_demos=4, max_rounds=1, teacher_settings=dict(lm=gpt4)) # max_labeled_demos=8,

        metric = SimilarityScorer('models/wiki.en.vec')

        optimizer = BootstrapFewShot(metric=metric.score_prediction, **config) # metric.score_prediction
        prog = optimizer.compile(Mod(), trainset=self.examples)
        evaluate = Evaluate(devset=self.examples, metric=metric.score_prediction, num_threads=4, display_progress=True, display_table=0) # metric.score_prediction
        evaluate(prog)
        self.module = prog
        prog.save(compiled_state_filepath)

    def load(self):
        # If filepath exists
        if os.path.exists(self.compiled_state_filepath):
            self.module.load(self.compiled_state_filepath)
        return