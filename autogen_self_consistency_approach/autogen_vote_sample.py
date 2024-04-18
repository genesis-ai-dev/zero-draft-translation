import autogen
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from autogen.agentchat.conversable_agent import Agent, initiate_chats
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
# from autogen.agentchat.contrib.capabilities import TransformMessages, transforms
from dotenv import load_dotenv
import os
import json
import chromadb
from typing_extensions import Annotated
# from ModelClient import AnthropicClient
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union
import chromadb.utils.embedding_functions as embedding_functions
import sacrebleu

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
# anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai_api_key,
                model_name="text-embedding-3-small"
            )

config_list = [
    {
        'model': 'gpt-4-turbo',
        'api_key': openai_api_key
    },
    
]

llm_config = {
    'timeout': 600,
    # 'seed': 42,
    'config_list': config_list,
    'temperature': 0
}


def termination_msg(x):
    return isinstance(x, dict) and 'TERMINATE' == str(x.get('content', ''))[-9:].upper()

num_agents = 20
source_language = 'English'
target_language = os.getenv('TARGET_LANGUAGE')
passage = 'In the beginning, God created the heavens and the earth.'

boss = UserProxyAgent(
    name='Boss',
    system_message=f"""
    'You assign a passage to your team to translate from {source_language} to {target_language}.'
    """,
    # Will eventually need to ask them to vote as well?
    is_termination_msg=termination_msg,
    human_input_mode='NEVER',
    code_execution_config=False,
    default_auto_reply='Reply `TERMINATE` if the task is done.',
    description='The boss who assigns translation tasks to a team of agents.',
)

librarian = RetrieveUserProxyAgent(
    name='Librarian',
    is_termination_msg=termination_msg,
    human_input_mode='NEVER',
    max_consecutive_auto_reply=3,
    retrieve_config={
        'task': 'qa',
        'docs_path': [
            os.path.join(os.path.abspath(''), 'dictionary', 'target_training_dataset_formatted.txt'),
            os.path.join(os.path.abspath(''), 'dictionary', 'english-target-dialogs-drills.txt'),
            os.path.join(os.path.abspath(''), 'dictionary', 'quran_english_target.txt'),
            os.path.join(os.path.abspath(''), 'dictionary', 'target_dictionary.json'),
        ],
        'custom_text_types': ['txt', 'json'], ## Not included in example
        'chunk_token_size': 2000,
        'model': config_list[0]['model'],
        'must_break_at_empty_line': False, ## Not included in example
        'client': chromadb.PersistentClient(path='/tmp/chromadb'),
        'collection_name': 'groupchat',
        'embedding_model': 'all-mpnet-base-v2', ## Not included in example
        'embedding_function': openai_ef, ## Not included in example
        'get_or_create': True,
        # 'customized_prompt': f'Retrieve many brief and relevant excerpts from resources needed to translate the following text from {source_language} to {target_language}: "{passage}"',
    },
    code_execution_config=False,
    description='Assistant who has extra content retrieval power for looking up words and sentence structure.',
)

def retrieve_example_content(
    message: Annotated[
        str,
        'Refined message which keeps the original meaning and can be used to retrieve content for translation question answering.'
    ],
    n_results: Annotated[int, 'Number of results'] = 3,
) -> str:
    librarian.n_results = n_results # Number of results to retrieve
    # Check if the content needs updating
    update_context_case1, update_context_case2 = librarian._check_update_context(message)
    if (update_context_case1 or update_context_case2) and librarian.update_context:
        librarian.problem = message if not hasattr(librarian, 'problem') else librarian.problem
        _, ret_msg = librarian._generate_retrieve_user_reply(message)
    else:
        _context = {'problem': message, 'n_results': n_results}
        ret_msg = librarian.message_generator(librarian, None, _context)
    return ret_msg if ret_msg else message

librarian.human_input_mode = 'NEVER' # Disable human input for boss aid since it only retrieves data

def retrieve_dictionary_content(
    message: str,
    n_results_per_word: int = 8,
) -> str:
    with open('dictionary/target_dictionary.json', 'r', encoding='utf-8') as file:
        dictionary = json.load(file)
    words = message.split()
    relevant_entries = []
    for word in words:
        word_relevant_entries = []
        for entry in dictionary:
            entry_text = f"{entry.get('word', '')} {entry.get('definition', '')} {entry.get('example', '')} {entry.get('translation', '')}"
            if word.lower() in entry_text.lower():
                word_relevant_entries.append(entry)
                if len(word_relevant_entries) == n_results_per_word:
                    break
        relevant_entries.extend(word_relevant_entries)
    
    # Converting the dictionary entries to a string format for return
    return json.dumps(relevant_entries, indent=2, ensure_ascii=False)



sampling_lead = ConversableAgent(
    name='Sampling Lead',
    system_message=f'You are the lead of the sampling team.',
    llm_config={'config_list': config_list},
    description='The lead of the sampling team.',
    human_input_mode='NEVER',
)

# voting_lead = ConversableAgent(
#     name='Sampling Lead',
#     system_message=f'You are the lead of the voting team.',
#     llm_config={'config_list': config_list},
#     description='The lead of the voting team.',
#     human_input_mode='NEVER',
# )

translations = []
def store_translations(recipient, sender, third_arg):
    # if recipient.success:
    translation = sender.last_message(recipient)['content'].strip().strip('"')
    translations.append(translation)
    print(f'Translation stored from {sender.name}: {translation}')
    return ''

# votes = []
# def store_votes(recipient, sender, third_arg):
#     # if recipient.success:
#     translations.append(sender.last_message(recipient)['content'])
#     print(f'Translation stored from {sender.name}: {sender.last_message(recipient)['content']}')
#     return ''


sampling_agents = []
for i in range(num_agents):
    sampling_agents.append(ConversableAgent(
        name=f'Translator {i}', 
        system_message=f'You are an expert at translating from {source_language} to {target_language}.', 
        llm_config={'config_list': config_list}, 
        # is_termination_msg=termination_msg, 
        human_input_mode='NEVER', 
        code_execution_config=False, 
        # default_auto_reply='Reply `TERMINATE` if the task is done.', 
        description=f'Translator {i} who is assigned a translation task.',
        ))


for caller in sampling_agents:
    d_retrieve_content = caller.register_for_llm(
        description=f'Retrieve content for answering questions regarding translating between {source_language} and {target_language}.',
        api_style='function'
    )(retrieve_dictionary_content)

sampling_lead.register_for_execution()(d_retrieve_content)

# for caller in sampling_agents:
#     d_retrieve_content = caller.register_for_llm(
#         description=f'Retrieve content for answering questions regarding translating between {source_language} and {target_language}.',
#         api_style='function'
#     )(retrieve_example_content)

# sampling_lead.register_for_execution()(d_retrieve_content)


sampling_chats = []    
for i, agent in enumerate(sampling_agents):
    chat = {
        'recipient': agent,
        'message': f'Retrieve content and translate the following from {source_language} to {target_language}: {passage}. Just provide the {target_language} translation, nothing else.',
        'max_turns': 2,
        'summary_method': store_translations,
    }
    sampling_chats.append(chat)

sampling_lead.register_nested_chats(
    sampling_chats,
    trigger=boss,
)

boss.initiate_chats(
    [
        {
            'recipient': sampling_lead,
            'message': 'Assign the translation task to the team.',
            'max_turns': 1,
            'summary_method': None,
        }
    ]
)


[print(translation) for translation in translations]

def top_bleu_sentences(sentences: list, n: int) -> list:
    # Calculate BLEU scores for each sentence against all others
    bleu_scores = {}
    for i, candidate in enumerate(sentences):
        references = [ref for j, ref in enumerate(sentences) if i != j]
        score = sacrebleu.sentence_bleu(candidate, references).score
        bleu_scores[sentences[i]] = score

    # Sort sentences by their BLEU score in descending order
    sorted_sentences = sorted(bleu_scores, key=bleu_scores.get, reverse=True)

    # Return the top n distinct sentences with the highest scores
    return sorted_sentences[:n]

top_translations = top_bleu_sentences(translations, 3)

print('\nTop translations:')
[print(translation) for translation in top_translations]