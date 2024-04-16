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

dspy.settings.configure(lm=local_llm)


class Pirate(dspy.Signature):
    """Translate the input Bible verse into Pirate speak."""
    verse = dspy.InputField()
    pirate_verse = dspy.OutputField()


class Mod(dspy.Module):
    def __init__(self):
        super().__init__()
        
        self.translate = dspy.ChainOfThought(Pirate)

    def forward(self, verse):
        return self.translate(verse=verse, temperature=0.2)
    

class Translate():
    def __init__(self, compile=False):
        self.module = Mod()
        self.compiled_state_filepath = 'compiled_states/compiled_state_pirate.json'
        
        pirate_examples = [
            dspy.Example(
                verse='In the beginning God created the heaven and the earth.',
                pirate_verse="In the beginnin', Cap'n God fashioned the heavens and the earth from the void."
            ),
            dspy.Example(
                verse='Then I bathed you with water, washed all the blood off of you, and put oil on you.',
                pirate_verse="Then I bathed ye with water, scrubbed all the blood off ye, and slathered ye in oil, ye scallywag."
            ),
            dspy.Example(
                verse='Whoso loveth instruction loveth knowledge: but he that hateth reproof is brutish.',
                pirate_verse="Whoever cherishes learnin' loves the treasure of knowledge, but he who spurns a good scoldin' be a daft lubber."
            ),
            dspy.Example(
                verse='Even when walking through the dark valley of death I will not be afraid, for you are close beside me, guarding, guiding all the way.',
                pirate_verse="Even when treadin' through the shadowy valley of death, I'll not fear, for ye be by me side, guidin' and guardin' me with yer rod and staff."
            ),
            dspy.Example(
                verse='Mine heritage is unto me as a lion in the forest; it crieth out against me: therefore have I hated it.',
                pirate_verse="Me heritage be unto me as a lion in the jungle; it roars against me: hence, I've taken a dislike to it."
            ),
            dspy.Example(
                verse='For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.',
                pirate_verse="For the great Cap'n above so adored this world that he gave his one and only Son, that any soul believin' in him shan't perish but have everlasting life."
            ),
            dspy.Example(
                verse='I can do all things through Christ who strengthens me.',
                pirate_verse= "I can weather through all storms with Christ who gives me strength, arrr."
            ),
            dspy.Example(
                verse='Trust in the Lord with all your heart and lean not on your own understanding;',
                pirate_verse="Trust in the Lord with all yer heart and don't lean on yer own map; arr, she be misleading."
            ),
            dspy.Example(
                verse='The Lord is my shepherd, I lack nothing.',
                pirate_verse="The Lord be me shepherd, I want for nothin'."
            ),
            dspy.Example(
                verse='For the wages of sin is death, but the gift of God is eternal life in Christ Jesus our Lord.',
                pirate_verse="For the bounty for sin be death, but the gift of the Cap'n be eternal life in Christ Jesus our Lord."
            )
        ]

        self.examples = [x.with_inputs('verse') for x in pirate_examples]

        if compile:
            self.compile()
        else:
            self.load()
    

    def pirate_metric(self, example, prediction, trace=None):
        # Return 0-1 float score based on length difference where 1 is same length and 0 is half or double length
        # Calculate the lengths of the strings
        len1 = len(example.verse)
        len2 = len(prediction.pirate_verse)

        # Ensure we don't divide by zero
        if len1 == 0 or len2 == 0:
            return 0

        # Calculate the ratio of lengths (always > 1)
        length_ratio = max(len1, len2) / min(len1, len2)

        # Calculate the score based on length difference
        # Score is 1 if lengths are the same, and decreases to 0 if one is double the length of the other or half.
        score = max(0, 2 - length_ratio) / 1.0  # Divide by 1.0 to ensure the result is a float

        return score


    def compile(self):
        compiled_state_filepath = self.compiled_state_filepath
        config = dict(max_bootstrapped_demos=4, max_rounds=1, teacher_settings=dict(lm=gpt4)) # max_labeled_demos=8,

        metric = SimilarityScorer('models/wiki.en.vec')

        optimizer = BootstrapFewShot(metric=self.pirate_metric, **config)
        prog = optimizer.compile(Mod(), trainset=self.examples)
        evaluate = Evaluate(devset=self.examples, metric=self.pirate_metric, num_threads=4, display_progress=True, display_table=0)
        evaluate(prog)
        self.module = prog
        prog.save(compiled_state_filepath)

    def load(self):
        # If filepath exists
        if os.path.exists(self.compiled_state_filepath):
            self.module.load(self.compiled_state_filepath)
        return