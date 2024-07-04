import anthropic
import openai
import re
import os
from dotenv import load_dotenv

class Model:
    def __init__(self, api, model_name):
        self.api = api
        self.model_name = model_name
        self.client = self._get_client()

    def _get_client(self):
        load_dotenv()
        if self.api == "anthropic":
            return anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        elif self.api == "openai":
            return openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        else:
            raise ValueError(f"Unsupported API: {self.api}")

    def translate(self, source_lang, target_lang, closest_verses, verse):
        if self.api == "anthropic":
            return self._translate_anthropic(source_lang, target_lang, closest_verses, verse, target_script='appropriate')
        elif self.api == "openai":
            return self._translate_openai(source_lang, target_lang, closest_verses, verse, target_script='appropriate')

    def _translate_anthropic(self, source_lang, target_lang, closest_verses, verse, target_script='appropriate'):
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=1000,
            temperature=0,
            system=f"You are an expert at translation and can perfectly apply the translation principles demonstrated in these {source_lang} to {target_lang} resources:\n{closest_verses}",
            messages=[
                {
                    "role": "user",
                    "content": f"Translate the following into the {target_lang} language with {target_script} script and put the translation in double square brackets: \n{verse}"
                }
            ]
        )
        translation = re.search(r'\[\[(.*?)\]\]', message.content[0].text)
        return translation.group(1) if translation else "Translation not found"

    def _translate_openai(self, source_lang, target_lang, closest_verses, verse, target_script='appropriate'):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": f"You are an expert at translation and can perfectly apply the translation principles demonstrated in these {source_lang} to {target_lang} resources:\n{closest_verses}"},
                {"role": "user", "content": f"Translate the following into the {target_lang} language with {target_script} script and put the translation in double square brackets: \n{verse}"}
            ],
            max_tokens=1000,
            temperature=0
        )
        translation = re.search(r'\[\[(.*?)\]\]', response.choices[0].message.content)
        return translation.group(1) if translation else "Translation not found"