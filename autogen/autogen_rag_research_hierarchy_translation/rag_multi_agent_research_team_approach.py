import autogen
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from autogen.agentchat.conversable_agent import Agent, initiate_chats
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
# from autogen.agentchat.contrib.capabilities import TransformMessages, transforms
from dotenv import load_dotenv
import os
import chromadb
from typing_extensions import Annotated
# from ModelClient import AnthropicClient
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

config_list = [
    {
        'model': 'gpt-4',
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



target_gen_1_26 = """
"Na, phitharo si Allah, "Mbalayon tano on sa mga taw na rkano tano a kasimilar. 
Sogoon tano iran sa mga isda sa mga dagat ombay sa mga torogoy sa kalangitan. 
Sogoon tano iran sa mga binatang naa sa mga kalangan ombay sa mga binatang mala 
andao sa duta. Ombay sogoon tano iran sa toro toro nga mga binatang mioyag sa duna."
"""

english_gen_1_26 = """
Then God said, "Let us make human beings so that they are like us.
Let them rule over the fish in the seas and the birds in the sky. Let
them rule over the livestock and all the wild animals. And let them rule
over all the creatures that move along the ground."
"""

english_exo_20_13 = "Do not murder."

passage = english_gen_1_26
source_language = 'English'
target_language = 'Target'

problem = f"""Translate the following from {source_language} into {target_language}: 
{passage}
Explain the translation and provide the back translation of the translated text."""

boss = UserProxyAgent(
    name='Boss',
    system_message="""
    'You assign a passage to the Translator. 
    Then you assign the Translator\'s translation to the Back_translator.'
    Then you assess if the back translation is sufficiently close to the original passage.
    If sufficiently close, terminate. If not, repeat the process.
    """,
    is_termination_msg=termination_msg,
    human_input_mode='NEVER',
    code_execution_config=False,
    default_auto_reply='Reply `TERMINATE` if the task is done.',
    description='The boss who asks questions and gives tasks.',
)
# boss.register_model_client(model_client_cls=AnthropicClient)

boss_aid = RetrieveUserProxyAgent(
    name='Boss_Assistant',
    is_termination_msg=termination_msg,
    human_input_mode='NEVER',
    max_consecutive_auto_reply=20,
    retrieve_config={
        'task': 'qa',
        'docs_path': [
            os.path.join(os.path.abspath(''), 'dictionary', 'mlm_training_dataset_formatted.txt'),
            os.path.join(os.path.abspath(''), 'dictionary', 'english-target-resource.txt'),
            os.path.join(os.path.abspath(''), 'dictionary', 'quran_english_target.txt'),
            os.path.join(os.path.abspath(''), 'dictionary', 'mrw_dictionary.json')
        ],
        'custom_text_types': ['json', 'txt'], ## Not included in example
        'chunk_token_size': 2000,
        'model': config_list[0]['model'],
        'must_break_at_empty_line': False, ## Not included in example
        'client': chromadb.PersistentClient(path='/tmp/chromadb'),
        'collection_name': 'groupchat',
        'embedding_model': 'all-mpnet-base-v2', ## Not included in example
        'get_or_create': True,
    },
    code_execution_config=False,
    description='Assistant who has extra content retrieval power for looking up words and sentence structure.',
)

translator = ConversableAgent(
    name='Translator',
    is_termination_msg=termination_msg,
    system_message=f'You are an expert translator. You receive information from your lead researcher to translate from {source_language} into {target_language}.', # Reply `TERMINATE` in the end when everything is done.',
    llm_config= {'config_list': config_list},
    description=f'Senior translator who receives translation research information and can translate passages from {source_language} into {target_language}.',
    human_input_mode="NEVER",
)

back_translator = ConversableAgent(
    name='Back_Translator',
    is_termination_msg=termination_msg,
    system_message=f'You are an expert translator. You receive information from your lead researcher to translate from {target_language} into {source_language}. Reply `TERMINATE` in the end when everything is done.',
    llm_config= {'config_list': config_list},
    description=f'Senior translator who receives translation research information and can translate passages from {target_language} into {source_language}.',
    human_input_mode="NEVER",
)

translation_validator = ConversableAgent(
    name='Translation_Validator',
    is_termination_msg=termination_msg,
    system_message=f'You are a translation validator. You compare an original text with the back-translated translation of the text to assess the quality of the translation. Reply `TERMINATE` in the end when everything is done.',
    llm_config= {'config_list': config_list},
    description='Translation validator who compares original text with back-translated text to assess translation quality.',
    human_input_mode="NEVER",
)

research_team_lead = ConversableAgent(
    name='Research_Team_Lead',
    is_termination_msg=termination_msg,
    system_message=f"""You lead a team of research agents who can access resources for translating between {source_language} and {target_language}.
    Your job is to interview each researcher according to their specialization and extract the most relevant information from their research to provide to the translator according to what needs to be translated.
    Reply `TERMINATE` in the end when everything is done.
    """,
    llm_config= {'config_list': config_list},
    description=f'Research team lead who can find information needed to translate between {source_language} and {target_language}.',
    human_input_mode="NEVER",
)

specialization = 'vocabulary'
researcher_vocabulary = ConversableAgent(
    name=f'Researcher_{specialization.capitalize()}',
    is_termination_msg=termination_msg,
    system_message=f'You are a translation researcher specializing in {specialization}. You are able to lookup {specialization} information in resources for translating between {source_language} and {target_language}.', # Reply `TERMINATE` in the end when everything is done.',
    llm_config={'config_list': config_list},
    description=f'Researcher who can find {specialization} information for translating between {source_language} and {target_language}.',
    human_input_mode="NEVER",
)

specialization = 'syntax'
researcher_syntax = ConversableAgent(
    name=f'Researcher_{specialization.capitalize()}',
    is_termination_msg=termination_msg,
    system_message=f'You are a translation researcher specializing in {specialization}. You are able to lookup {specialization} information in resources for translating between {source_language} and {target_language}.', # Reply `TERMINATE` in the end when everything is done.',
    llm_config={'config_list': config_list},
    description=f'Researcher who can find {specialization} information for translating between {source_language} and {target_language}.',
    human_input_mode="NEVER",
)

specialization = 'pragmatics'
researcher_pragmatics = ConversableAgent(
    name=f'Researcher_{specialization.capitalize()}',
    is_termination_msg=termination_msg,
    system_message=f'You are a translation researcher specializing in {specialization}. You are able to lookup {specialization} information in resources for translating between {source_language} and {target_language}.', # Reply `TERMINATE` in the end when everything is done.',
    llm_config={'config_list': config_list},
    description=f'Researcher who can find {specialization} information for translating between {source_language} and {target_language}.',
    human_input_mode="NEVER",
)

specialization = 'translation'
researcher_translation = ConversableAgent(
    name=f'Researcher_{specialization.capitalize()}',
    is_termination_msg=termination_msg,
    system_message=f'You are a translation researcher specializing in {specialization}. You are able to lookup {specialization} information in resources for translating between {source_language} and {target_language}.', # Reply `TERMINATE` in the end when everything is done.',
    llm_config={'config_list': config_list},
    description=f'Researcher who can find {specialization} information for translating between {source_language} and {target_language}.',
    human_input_mode="NEVER",
)


def _reset_agents():
    boss.reset()
    boss_aid.reset()
    translator.reset()
    back_translator.reset()
    translation_validator.reset()
    research_team_lead.reset()
    researcher_vocabulary.reset()
    researcher_syntax.reset()
    researcher_pragmatics.reset()


_reset_agents()

def retrieve_content(
    message: Annotated[
        str,
        'Refined message which keeps the original meaning and can be used to retrieve content for translation question answering.'
    ],
    n_results: Annotated[int, 'Number of results'] = 3,
) -> str:
    boss_aid.n_results = n_results # Number of results to retrieve
    # Check if the content needs updating
    update_context_case1, update_context_case2 = boss_aid._check_update_context(message)
    if (update_context_case1 or update_context_case2) and boss_aid.update_context:
        boss_aid.problem = message if not hasattr(boss_aid, 'problem') else boss_aid.problem
        _, ret_msg = boss_aid._generate_retrieve_user_reply(message)
    else:
        _context = {'problem': message, 'n_results': n_results}
        ret_msg = boss_aid.message_generator(boss_aid, None, _context)
    return ret_msg if ret_msg else message

boss_aid.human_input_mode = 'NEVER' # Disable human input for boss aid since it only retrieves data


for caller in [researcher_vocabulary, researcher_syntax, researcher_pragmatics]:
    d_retrieve_content = caller.register_for_llm(
        description=f'Retrieve content for answering questions regarding translating between {source_language} and {target_language}.',
        api_style='function'
    )(retrieve_content)

# What is this small block even for? register_for_llm and register_for_execution seem to do the same thing
for executor in [boss, translator, back_translator, research_team_lead]:
    executor.register_for_execution()(d_retrieve_content)

allowed_transitions = {
    boss: [translator, back_translator],
    translator: [boss, research_team_lead],
    back_translator: [boss, research_team_lead],
    research_team_lead: [translator, back_translator],
}

groupchat = autogen.GroupChat(
    agents=[boss, translator, back_translator, research_team_lead],
    allowed_or_disallowed_speaker_transitions=allowed_transitions,
    speaker_transitions_type='allowed',
    messages=[],
    max_round=20,
    send_introductions=True, 
    # speaker_selection_method='round_robin', ##
    # allow_repeat_speaker=False,
)
        
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

def aggregate_summary_from_nested_chats(
        chat_queue: List[Dict[str, Any]], recipient: Agent, messages: Union[str, Callable], sender: Agent, config: Any
    ) -> Tuple[bool, str]:
        """An enhanced chat reply function.
        This function initiates one or a sequence of chats between the "recipient" and the agents in the
        chat_queue. It extracts and aggregates summaries from the nested chat based on the "summary_method"
        specified in each chat in chat_queue.

        Returns:
            Tuple[bool, str]: A tuple where the first element indicates the completion of the chat, and the second element contains the aggregated summary of all chats if any chats were initiated.
        """
        last_msg = messages[-1].get("content") if messages else ""
        chat_to_run = []
        for i, c in enumerate(chat_queue):
            current_c = c.copy()
            if current_c.get("sender") is None:
                current_c["sender"] = recipient
            message = current_c.get("message")
            # Use the last message from the original chat history as the first message in this nested chat (for the first chat in the chat queue), if message is not provided.
            if message is None and i == 0:
                message = last_msg
            if callable(message):
                message = message(recipient, messages, sender, config)
            # Run chat that has a valid message.
            if message:
                current_c["message"] = message
                chat_to_run.append(current_c)
        if not chat_to_run:
            return True, "No relevant information was found in the nested chats."

        # Initiate the chats and collect summaries
        res = initiate_chats(chat_to_run)
        aggregated_summaries = " ".join([chat.summary for chat in res if chat.summary])

        return True, aggregated_summaries if aggregated_summaries else "No summaries were generated from the nested chats."


nested_chats_research_translation = [
    {
        'recipient': researcher_vocabulary,
        'max_turns': 2,
        'message': f'What are all the relevant vocabulary pairs needed to translate the following from {source_language} into {target_language}: {passage}?',
        'summary_method': 'last_msg', # 'reflection_with_llm
        'summary_prompt': 'Extract the relevant vocabulary pairs relevant for the desired translation.',
    },
    {
        'recipient': researcher_syntax,
        'max_turns': 2,
        'message': f'What is all the syntax information needed to translate the following from {source_language} into {target_language}: {passage}?',
        'summary_method': 'last_msg', # 'reflection_with_llm
        'summary_prompt': 'Extract the syntax information relevant for the desired translation.',
    },
    {
        'recipient': researcher_pragmatics,
        'max_turns': 2,
        'message': f'What is all the grammatical information needed to translate the following from {source_language} into {target_language}: {passage}?',
        'summary_method': 'last_msg', # 'reflection_with_llm
        'summary_prompt': 'Extract the grammar rules relevant for the desired translation.',
    },
    {
        'recipient': researcher_translation,
        'max_turns': 1,
        'message': f'With all the context provided, provide a translation of the following passage from {source_language} into {target_language} after giving a thorough report of your rationale: {passage}?',
        'summary_method': 'last_msg', # 'reflection_with_llm
        'summary_prompt': 'Extract the grammar rules relevant for the desired translation.',
    },
]

def translated_passage(recipient, messages, sender, config):
    return recipient.chat_messages_for_summary(sender)[-1]['content']

nested_chats_research_back_translation = [
    {
        'recipient': researcher_vocabulary,
        'max_turns': 2,
        # 'message': f'What are all the relevant vocabulary pairs needed to translate the following from {target_language} into {source_language}: {translated_passage}?',
        'message': translated_passage,
        'summary_method': 'last_msg', # 'reflection_with_llm
        'summary_prompt': 'Extract the relevant vocabulary pairs relevant for the desired translation.',
    },
    {
        'recipient': researcher_syntax,
        'max_turns': 2,
        # 'message': f'What is all the syntax information needed to translate the following from {target_language} into {source_language}: {translated_passage}?',
        'message': translated_passage,
        'summary_method': 'last_msg', # 'reflection_with_llm
        'summary_prompt': 'Extract the syntax information relevant for the desired translation.',
    },
    {
        'recipient': researcher_pragmatics,
        'max_turns': 2,
        # 'message': f'What is all the pragmatic information needed to translate the following from {target_language} into {source_language}: {translated_passage}?',
        'message': translated_passage,
        'summary_method': 'last_msg', # 'reflection_with_llm
        'summary_prompt': 'Extract the pragmatics relevant for the desired translation.',
    },
    {
        'recipient': researcher_translation,
        'max_turns': 1,
        # 'message': f'With all the context provided, provide a translation of the following passage from {target_language} into {source_language} after giving a thorough report of your rationale: {translated_passage}?',
        'message': translated_passage,
        'summary_method': 'last_msg', # 'reflection_with_llm
        'summary_prompt': f'Provide a translation of the passage from {target_language} into {source_language} after giving a thorough report of your rationale',
    },
]

research_team_lead.register_nested_chats(
    nested_chats_research_translation,
    # reply_func_from_nested_chats=aggregate_summary_from_nested_chats,
    # trigger=lambda sender: sender in [translator],
    trigger=translator
)


research_team_lead.register_nested_chats(
    nested_chats_research_back_translation,
    # reply_func_from_nested_chats=aggregate_summary_from_nested_chats,
    trigger=back_translator
)

nested_chats_translation_consultation = [
    {
        'recipient': research_team_lead,
        'max_turns': 1,
        # 'message': f'Provide the translation of the following passage from {source_language} into {target_language} without any additional commentary or explanation - just the translation: {passage}',
        'summary_method': 'reflection_with_llm', # 'last_msg
        'summary_prompt': 'Provide the translator with the most relevant information for translating the passage.',
    }
]

translator.register_nested_chats(
    nested_chats_translation_consultation,
    reply_func_from_nested_chats=aggregate_summary_from_nested_chats,
    trigger=boss,
)

nested_chats_back_translation_consultation = [
    {
        'recipient': research_team_lead,
        'summary_method': 'last_msg', # 'reflection_with_llm
        'summary_prompt': 'Provide the back translator with the most relevant information for translating the passage.',
    }
]

back_translator.register_nested_chats(
    nested_chats_translation_consultation,
    reply_func_from_nested_chats=aggregate_summary_from_nested_chats,
    trigger=boss,
)

# reply = boss.generate_reply(
#     messages=[
#         {
#             'role': 'user',
#             'content': problem
#         }
#     ]
# )

# Start chatting with the boss as this is the user proxy agent.
# boss.initiate_chat(
#     manager,
#     message=problem,
# )

boss.initiate_chats(
    [
        {
            'recipient': translator,
            'message': f'Translate the following from {source_language} into {target_language} with zero additional commentary or explanation - just the {target_language} translation: {passage}',
            'max_turns': 1,
            'summary_method': 'last_msg', # 'reflection_with_llm',
        },
        {
            'recipient': back_translator,
            'message': f'Translate the recent {target_language} translation back into {source_language} once you have explained your rationale: ',
            # 'message': translated_passage,
            'max_turns': 1,
            'summary_method': 'last_msg', # 'reflection_with_llm',
        },
        {
            'recipient': translation_validator,
            'message': 'Compare the original text with the back-translated text to assess the quality of the translation.',
            'max_turns': 1,
            'summary_method': 'last_msg',
        },
    ]
)

