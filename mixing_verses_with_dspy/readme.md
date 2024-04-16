# Bible Verse Translation Enhancement Tool

## Overview
This tool is designed to generate new Bible verses which exist as a conglomeration of three existing translations (from the ebible corpus).It leverages language models and various algorithms and custom metrics to evaluates them against existing versions.

## Findings
In general the script is effective at generating new verses, but there remains an issue of consistency among multiple generated verses. For example, including the KJV amongst modern translations can yield modern sounding verses with the occasional 'thee' or 'hast' slipped in.
The following models yielded these ratings with the current metric in the code:
**Mixtral:** 13.8%, 19.8%
**Intel Neural Chat:** 86.0%, 84.1%
	st: 70.4%
**AbacusAI Giraffe:** 94.6%, 94.6%
	st: 86.2%
**Laser Dolphin:** 91.9%, 90.8%
**Abacus Smaug:** 94.6%
	st: 87.5%

## Features
- **Verse Generation**: Generate new verses by blending three different Bible versions.
- **Download Utility**: Automatically download Bible texts from specified URLs.
- **Similarity Calculation**: Calculate the similarity between the newly generated verses and the original verses using multiple metrics.
- **Customizable Language Models**: Allows selection of different language models for generating translations.
- **Evaluation Metrics**: Utilizes a combination of similarity and diversity metrics to evaluate verse quality.

## Prerequisites
- Python 3.x
- Libraries: `requests`, `matplotlib`, `fuzzywuzzy`, `dspy`, `dotenv`, `gensim`, `sentence-transformers`
- OpenAI API key

## Installation
Ensure that Python 3 and pip are installed on your system. Then, install the necessary Python libraries and configure your environment:
```bash
pip install requests matplotlib fuzzywuzzy python-dotenv gensim sentence-transformers
```

Follow specific installation instructions for the dspy library.

## Setup
Set up your environment by storing your OpenAI API key in a .env file:
```bash
OPENAI_API_KEY='your_api_key_here'
```
To use a local model, LMStudio can be used to host at **`http://localhost:1234/v1`**
Set the desired model in **`DSPyMix.py`** here:
```bash
# Set model here
dspy.settings.configure(lm=local_llm) # or gpt3, gpt4, etc. as defined
```

## Usage
1. Ensure all URLs in the script are accessible and point to the correct locations of the Bible text files.
2. Configure the desired language model and translation settings in the script.
3. Execute the main Python script:
```bash
python your_script_name.py
```

## How It Works
- **Downloading Texts:** The script begins by downloading Bible texts from predefined URLs.
- **Generating Verses:** Uses the **`Mix`** class to create new verses by blending three different versions. The **`Mix`** class can be customized to use different language models, such as GPT-3.5 or GPT-4, affecting the style and quality of the generated verses.
 - **Calculating Similarity:** After generating new verses, the script calculates similarity using the **`VerseMetric`** class, which combines Word2Vec, Sentence Transformers, and FuzzyWuzzy metrics. This class allows for manual adjustments of weights to fine-tune evaluation criteria based on semantic similarity, structural diversity, and length similarity.

## Customizing Mix and VerseMetric
- **Mix Class:** Instantiate with **`compile=True`** to compile models based on examples or **`compile=False`** to load precompiled states. It uses a series of examples to train or evaluate the model's performance in mixing verse translations.
- **VerseMetric Class:** Adjust the weights of different metrics like Word2Vec and Sentence Transformers to prioritize certain aspects of similarity or diversity in the evaluations.

## Output
Includes:

- Newly generated verses.
- Calculated similarities and diversities for these verses.
- A plot showing various metrics across the verses.

