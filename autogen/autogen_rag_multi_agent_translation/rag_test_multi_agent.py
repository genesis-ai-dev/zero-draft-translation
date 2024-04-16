import autogen
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
# from autogen.agentchat.contrib.capabilities import TransformMessages, transforms
from dotenv import load_dotenv
import os
import chromadb
from typing_extensions import Annotated
# from ModelClient import AnthropicClient

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

config_list = [
    # {
    #     # Choose your model name.
    #     "model": "claude-3-opus-20240229",
    #     # You need to provide your API key here.
    #     "api_key": anthropic_api_key,
    #     "base_url": "https://api.anthropic.com",
    #     "api_type": "anthropic",
    #     "model_client_cls": "AnthropicClient",
    # },
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

source_language = 'English'
target_language = 'Enter target language here'

target_gen_1_26 = """
Enter target language passage here
"""

english_gen_1_26 = """
Then God said, "Let us make human beings so that they are like us.
Let them rule over the fish in the seas and the birds in the sky. Let
them rule over the livestock and all the wild animals. And let them rule
over all the creatures that move along the ground."
"""

english_exo_20_13 = "Do not murder."

passage = english_exo_20_13

boss = UserProxyAgent(
    name='Boss',
    system_message='You return to me all the translation information I give you.',
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
    max_consecutive_auto_reply=3,
    retrieve_config={
        'task': 'qa',
        'docs_path': [
            os.path.join(os.path.abspath(''), 'dictionary', 'training_training_dataset_formatted.txt'),
            os.path.join(os.path.abspath(''), 'dictionary', 'english-target-resource.txt'),
            os.path.join(os.path.abspath(''), 'dictionary', 'quran_english_target.txt')
        ],
        'custom_text_types': ['txt'], ## Not included in example
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
# boss_aid.register_model_client(model_client_cls=AnthropicClient)

translator_llm_config = llm_config.copy()
# translator = AssistantAgent(
translator = ConversableAgent(
    name='Senior_Translator',
    is_termination_msg=termination_msg,
    system_message='You are a senior translator, you take grammar and instruction on how to translate and produce the best translation for a passage. Reply `TERMINATE` in the end when everything is done.',
    llm_config= {'config_list': config_list},
    description=f'Senior translator who can translate passages from {source_language} into {target_language}.',
    human_input_mode="NEVER",
)
# translator.register_model_client(model_client_cls=AnthropicClient)

researcher_llm_config = llm_config.copy()
# researcher = AssistantAgent(
researcher = ConversableAgent(
    name='Researcher',
    is_termination_msg=termination_msg,
    system_message=f"""You are a researcher specializing in low-resource language. 
    You look through dictionaries and dialogs containing both {source_language} and {target_language}. 
    You provide a thorough report of why certain words were chosen and how the translation was done.
    """,
    # Reply `TERMINATE` in the end when everything is done.
    llm_config= {'config_list': config_list},
    description='Researcher who can look up words and sentence structure in dictionaries and dialogs.',
    human_input_mode="NEVER",
)

editor_llm_config = llm_config.copy()
# editor = AssistantAgent(
editor = ConversableAgent(
    name='Editor',
    is_termination_msg=termination_msg,
    system_message=f'You are an editor, you can edit the translation from {source_language} into {target_language} and make it better, after providing a thorough explanation of your rationale. Reply `TERMINATE` in the end when everything is done.',
    llm_config={'config_list': config_list},
    description=f'Editor who can edit and improve translations from {source_language} into {target_language}.',
    human_input_mode="NEVER",
)
# editor.register_model_client(model_client_cls=AnthropicClient)

# Make back translator agent
back_translator_config = llm_config.copy()
# back_translator = AssistantAgent(
back_translator = ConversableAgent(
    name='Back_Translator',
    is_termination_msg=termination_msg,
    system_message=f'You are a back translator, you can back translate the translation from {target_language} back into {source_language}, after providing a thorough explanation of your rationale. Reply `TERMINATE` in the end when everything is done.',
    llm_config={'config_list': config_list},
    description=f'Back translator who can back translate translations into {source_language}.',
    human_input_mode="NEVER",
)
# back_translator.register_model_client(model_client_cls=AnthropicClient)

critic_config = llm_config.copy()
# critic = AssistantAgent(
critic = ConversableAgent(
    name='Critic',
    is_termination_msg=termination_msg,
    system_message='You are a critic and find legitimate faults in the work of your agent collegues Reply `TERMINATE` in the end when everything is done.',
    llm_config={'config_list': config_list},
    description='Critic who finds valid faults in proposed translations.',
    human_input_mode="NEVER",
)

problem = f"""Translate the following from {source_language} into {target_language}: 
{passage}
Explain the translation and provide the back translation of the translated text."""
# 

def _reset_agents():
    boss.reset()
    boss_aid.reset()
    researcher.reset()
    translator.reset()
    editor.reset()
    back_translator.reset()
    critic.reset()

def call_rag_chat():
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

    # context_handling = TransformMessages(
    #     transforms=[
    #         transforms.MessageHistoryLimiter(max_messages=10),
    #         transforms.MessageTokenLimiter(max_tokens=1000, max_tokens_per_message=50),
    #     ]
    # )

    for caller in [researcher, translator, editor, back_translator, critic]:
        d_retrieve_content = caller.register_for_llm(
            description=f'Retrieve content for answering questions regarding translating between {source_language} and {target_language}.',
            api_style='function'
        )(retrieve_content)
        # caller.register_model_client(model_client_cls=AnthropicClient)
        # context_handling.add_to_agent(caller)

    for executor in [boss, translator]:
        executor.register_for_execution()(d_retrieve_content)

    groupchat = autogen.GroupChat(
        agents=[boss, researcher, translator, editor, back_translator, critic],
        messages=[],
        max_round=20,
        # send_introductions=True, 
        speaker_selection_method='round_robin', ##
        allow_repeat_speaker=False,
    )
            
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Start chatting with the boss as this is the user proxy agent.
    # boss.initiate_chat(
    #     manager,
    #     message=problem,
    # )

    # Try sequential chat
    boss.initiate_chats(

        [
            {
                'recipient': researcher,
                'message': f'Find all the words and information about sentence structure a translator would need to translate the following from {source_language} into {target_language} and provide your rationale: {passage}',
                'max_turns': 2,
                # 'summary_method': 'last_msg',
                'summary_method': 'reflection_with_llm',
            },
            {
                'recipient': translator,
                'message': f'Translate the following from {source_language} into {target_language} after providing your rationale: {passage}',
                'max_turns': 2,
                # 'summary_method': 'last_msg',
                'summary_method': 'reflection_with_llm',
            },
            {
                'recipient': editor,
                'message': f'Edit the translation from {source_language} into {target_language} and make it better after providing your rationale.',
                'max_turns': 2,
                # 'summary_method': 'last_msg',
                'summary_method': 'reflection_with_llm',
            },
            {
                'recipient': back_translator,
                'message': f'Back translate the translation from {target_language} back into {source_language} after providing your rationale (in English).',
                'max_turns': 2,
                # 'summary_method': 'last_msg',
                'summary_method': 'reflection_with_llm',
            }
        ]
    )

call_rag_chat()