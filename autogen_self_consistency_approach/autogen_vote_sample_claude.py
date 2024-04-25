import autogen
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from autogen.agentchat.conversable_agent import Agent, initiate_chats
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.qdrant_retrieve_user_proxy_agent import QdrantRetrieveUserProxyAgent
from qdrant_client import QdrantClient
# from autogen.agentchat.contrib.capabilities import TransformMessages, transforms
from dotenv import load_dotenv
import os
import re
import json
import chromadb
from typing_extensions import Annotated
# from ModelClient import AnthropicClient
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union
import chromadb.utils.embedding_functions as embedding_functions
import sacrebleu
from Translations import Samples
from ModelClient import AnthropicClient
from Resources import TextFileProcessor
import tiktoken
from Levenshtein import ratio
from CustomRetrieveUserProxyAgent import CustomRetrieveUserProxyAgent


if __name__ == '__main__':
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')


    config_list = [
        {
            # Choose your model name.
            "model": "claude-3-haiku-20240307",
            # "model": "claude-3-opus-20240229",
            # You need to provide your API key here.
            "api_key": anthropic_api_key,
            "base_url": "https://api.anthropic.com",
            "api_type": "anthropic",
            "model_client_cls": "AnthropicClient",
        },
        # {
        #     'model': 'gpt-4-32k',
        #     'api_key': openai_api_key,
        # }    
    ]

    def termination_msg(x):
        return isinstance(x, dict) and 'TERMINATE' == str(x.get('content', ''))[-9:].upper()

    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=openai_api_key,
                    model_name="text-embedding-ada-002"
                )

    num_agents = 8
    source_language = 'English'
    target_language = os.getenv('TARGET_LANGUAGE')
    passage = 'Then God said, \"Let us make mankind in our image, in our likeness, so that they may rule over the fish in the sea and the birds in the sky, over the livestock and all the wild animals, and over all the creatures that move along the ground.\"'


    client = chromadb.PersistentClient(path='/tmp/chromadb')
    # qdrant_client = QdrantClient(":memory:")

    def text_split(text: str) -> List[str]:
        # Updated regex to better capture sentences or larger text blocks without curly braces
        pattern = r'\{(?:[^{}]*|\{[^{}]*\})*\}|[^{}]+'

        # Find all matches for the pattern in the text
        parts = re.findall(pattern, text, re.DOTALL)

        result = []
        for part in parts:
            num_lines = 1
            # Remove leading and trailing spaces and newlines
            part = part.strip()
            # Split the non-brace part by two lines
            lines = part.split('\n')
            for i in range(0, len(lines), num_lines):
                combined_lines = '\n'.join(lines[i:i+num_lines]).strip()
                if combined_lines:  # Make sure not to add empty strings
                    result.append(combined_lines)
                # if result:  # Check if result has items to avoid out-of-index errors
            # print(f'chunk: {result[-1]}')

        return result

    files = [
        os.path.join(os.path.abspath(''), 'dictionary', 'target_training_dataset_joined.txt'),
        os.path.join(os.path.abspath(''), 'dictionary', 'quran_english_target_joined.txt'),
        os.path.join(os.path.abspath(''), 'dictionary', 'target_dictionary.txt'),
    ]

    # resources = TextFileProcessor(
    #     file_paths=files,
    #     text_split_function=text_split,
    # )

    librarian = CustomRetrieveUserProxyAgent(
        name='Librarian',
        is_termination_msg=termination_msg,
        human_input_mode='NEVER',
        max_consecutive_auto_reply=3,
        code_execution_config=False,
        description='Assistant who has extra content retrieval power for looking up words and sentence structure.',
        retrieve_config={
            'task': 'qa',
            'docs_path': files, # resources.temp_files,
            # 'custom_text_types': ['txt'], 
            'model': config_list[0]['model'],
            'must_break_at_empty_line': False, ## Not included in example
            'client': client,
            'embedding_function': openai_ef, ## Not included in example
            # 'get_or_create': True,
            'context_max_tokens':50000,
            'custom_text_split_function': text_split,
            # 'chunk_mode': 'one_line',
        },
    )



    librarian.human_input_mode = 'NEVER' # Disable human input for librarian since it only retrieves data


    def retrieve_example_content(
        message: Annotated[
            str,
            'Refined message which keeps the original meaning and can be used to retrieve content for translation question answering.'
        ],
        n_results: Annotated[int, 'Number of results'] = 20,
    ) -> str:
        librarian.n_results = 20, # n_results # Number of results to retrieve
        # librarian._max_tokens = 200 # Overriding default value of 4000 when non oia model used
        # Check if the content needs updating
        update_context_case1, update_context_case2 = librarian._check_update_context(message)
        if (update_context_case1 or update_context_case2) and librarian.update_context:
            print(f'Updating context for librarian with message: {message}')
            librarian.problem = message if not hasattr(librarian, 'problem') else librarian.problem
            _, ret_msg = librarian._generate_retrieve_user_reply(message)
        else:
            print(f'Not updating context for librarian with message: {message}')
            _context = {'problem': message, 'n_results': n_results}
            ret_msg = librarian.message_generator(librarian, None, _context)
        return ret_msg if ret_msg else message


    user_proxy = UserProxyAgent(
        name='user_proxy',
        human_input_mode='NEVER',
        code_execution_config=False,
        is_termination_msg=termination_msg,
        system_message=f"""
        'You assign a passage to your team to translate from {source_language} to {target_language}.'
        """,
        # Will eventually need to ask them to vote as well?
        # default_auto_reply='Reply `TERMINATE` if the task is done.',
        description='The boss who assigns translation and voting tasks to other team leads.',
    )


    def retrieve_dictionary_content(
        message: str,
        n_results_per_word: int = 4,
    ) -> str:
        with open('dictionary/target_dictionary.json', 'r', encoding='utf-8') as file:
            dictionary = json.load(file)
        
        words = message.split()
        relevant_entries = []
        for word in words:
            word_relevant_entries = []
            # Use a dictionary to store entries and their similarity scores
            similarity_scores = {}
            
            for entry in dictionary:
                entry_text = f"{entry.get('word', '')} {entry.get('definition', '')} {entry.get('example', '')} {entry.get('translation', '')}"
                # Calculate similarity score
                score = ratio(word.lower(), entry_text.lower())
                similarity_scores[entry_text] = score
            
            # Find the entries with the highest similarity scores
            sorted_entries = sorted(similarity_scores.items(), key=lambda item: item[1], reverse=True)
            top_entries = [entry for entry, score in sorted_entries[:n_results_per_word]]
            
            relevant_entries.extend(top_entries)

        # Converting the dictionary entries to a string format for return
        return json.dumps(relevant_entries, indent=2, ensure_ascii=False)



    sampling_lead = ConversableAgent(
        name='Sampling Lead',
        system_message=f'You are the lead of the sampling team.',
        llm_config={'config_list': config_list},
        description='The lead of the sampling team.',
        human_input_mode='NEVER',
    )
    # sampling_lead.reset()



    voting_lead = ConversableAgent(
        name='Sampling Lead',
        system_message=f'You are the lead of the voting team.',
        llm_config={'config_list': config_list},
        description='The lead of the voting team.',
        human_input_mode='NEVER',
    )
    # voting_lead.reset()



    translations = Samples(method='top_bleu')

    def store_translations(recipient, sender, third_arg):
        full_message = sender.last_message(recipient)
        print(f'Full message received in store_translations: {full_message}')

        message = sender.last_message(recipient).get('content')
        if message and '[' in message and ']' in message:
            try:
                translation = [match for match in re.findall(r'\[(.*?)\]', message)][-1].strip().strip('"')
                translations.add_sample(translation)
                print(f'Translation stored from {sender.name}: {translation}')
            except IndexError:
                print(f"No valid translation found in the message from {sender.name}.")
        else:
            print(f"No translation brackets found in the message from {sender.name}.")

        return ''


    def store_votes(recipient, sender, third_arg):
        translations.submit_vote(sender.last_message(recipient)['content'])
        print(f'Vote cast from {sender.name}: {sender.last_message(recipient)['content']}')
        return ''


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
        

    voting_agents = []
    for i in range(num_agents):
        voting_agents.append(ConversableAgent(
            name=f'Bilingual interpreter {i}', 
            system_message=f'You are an expert at analyzing translations from {source_language} to {target_language}.', 
            llm_config={'config_list': config_list}, 
            # is_termination_msg=termination_msg, 
            human_input_mode='NEVER', 
            code_execution_config=False, 
            # default_auto_reply='Reply `TERMINATE` if the task is done.', 
            description=f'Bilingual interpreter {i} who is assigned the task of selecting the best translation from many options.',
            ))
        



    for caller in sampling_agents:
        d_retrieve_content_sample = caller.register_for_llm(
            name='retrieve_content',
            description=f'Retrieve content for answering questions regarding translating between {source_language} and {target_language}.',
            api_style='function'
        )(retrieve_example_content)

    sampling_lead.register_for_execution()(d_retrieve_content_sample)


    for caller in voting_agents:
        d_retrieve_content_vote = caller.register_for_llm(
            name='retrieve_content',
            description=f'Retrieve content for answering questions regarding translating between {source_language} and {target_language}.',
            api_style='function'
        )(retrieve_example_content)

    voting_lead.register_for_execution()(d_retrieve_content_vote)



    sampling_lead.register_model_client(model_client_cls=AnthropicClient)

    voting_lead.register_model_client(model_client_cls=AnthropicClient)

    for agent in sampling_agents:
        # agent.reset()
        agent.register_model_client(model_client_cls=AnthropicClient)
    for agent in voting_agents:
        # agent.reset()
        agent.register_model_client(model_client_cls=AnthropicClient)



    sampling_chats = []    
    for i, agent in enumerate(sampling_agents):
        chat = {
            'recipient': agent,
            'message': f'Retrieve content and translate the following from {source_language} to {target_language}: {passage}. Explain your reasoning first and end your response with only {target_language} translation in square brackets.',
            'max_turns': 2,
            'summary_method': store_translations,
        }
        sampling_chats.append(chat)

    sampling_lead.register_nested_chats(
        sampling_chats,
        trigger=user_proxy,
    )

    # Message must be a callable function in order for translations.top_bleu_samples to be live data (not empty data from when nested chat is registered)
    def voting_agent_callable_message(recipient, messages, sender, config):
        message = f'''
                Retrieve content only once to analyze the following translations from {source_language} to {target_language}: {translations.top_bleu_samples}. 
                Select the most natural and faithful translation of [\"{passage}\"] by providing your reasoning. 
                End your response with only square brackets containing only the designating letter of the best translation.'''
        return message

    voting_chats = []    
    for i, agent in enumerate(voting_agents):
        chat = {
            'recipient': agent,
            'message': voting_agent_callable_message,
            'max_turns': 2,
            'summary_method': store_votes,
        }
        voting_chats.append(chat)

    voting_lead.register_nested_chats(
        voting_chats,
        trigger=user_proxy,
    )

    # boss.register_model_client(model_client_cls=AnthropicClient)
    # librarian.register_model_client(model_client_cls=AnthropicClient)

    user_proxy.initiate_chats(
        [
            {
                'recipient': sampling_lead,
                'message': 'Assign the translation task to the team.',
                'max_turns': 1,
                'summary_method': None,
            },
            {
                'recipient': voting_lead,
                'message': 'Assign the voting task to the team.',
                'max_turns': 1,
                'summary_method': None,
            },
        ]
    )


    print(f'\nAll samples: {translations.all_samples}')
    print(f'\nTop BLEU samples: {translations.top_bleu_samples}')
    print(f'\nWinner: {translations.majority_vote}')



