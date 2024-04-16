import autogen
from autogen import ConversableAgent, GroupChat, GroupChatManager
# Set AUTOGEN_USE_DOCKER to "0/False/no" in your environment variables
from dotenv import load_dotenv
import os
# from DSPyMix import Mix
from DSPyPirate import Translate
# edited on linux machine
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# mix = Mix(compile=False)

translate = Translate(compile=False)

# Use type hints to help autogen use function as tool
# def mixed_verse_generator(verse_ver_1: str, verse_ver_2: str, verse_ver_3: str) -> str:
#     # Generate a new verse based on three incoming
#     new_verse = mix.module(verse_ver_1, verse_ver_2, verse_ver_3)
#     return new_verse.mixed_verse

def pirate_verse_generator(verse: str) -> str:
    # Generate a new verse based on three incoming
    new_verse = translate.module(verse)
    return new_verse.pirate_verse


config_list = [
    # {
    #     'model': '',
    #     'api_type': 'open_ai',
    #     'base_url': 'http://localhost:1234/v1',
    #     'api_key': 'NULL'
    # }
    {
        'model': 'gpt-4',
        'api_key': api_key
    }
]


llm_config = {
    'timeout': 600,
    'seed': 42,
    'config_list': config_list,
    'temperature': 0.2
}


team_lead = ConversableAgent(
    name='team_lead',
    llm_config=llm_config,
    system_message='You return to me the best pirate translation of a verse. When all agents are satisfied with the result, simply reply TERMINATE',
    human_input_mode='NEVER',
    is_termination_msg=lambda x: x.get('context', '').rstrip().endswith('TERMINATE')
)
team_lead.description = 'Coordinate the team of agents to produce the best pirate translation of a verse, and move on to the next verse.'

translator = ConversableAgent(
    name='translator',
    llm_config=llm_config, 
    system_message="You are an expert at translating Bible verses into pirate speak.",
    human_input_mode='NEVER',
    is_termination_msg=lambda x: x.get('context', '').rstrip().endswith('TERMINATE')
)
translator.description = 'Translate a Bible verse input into pirate speak.'


evaluator = ConversableAgent(
    name='evaluator',
    llm_config=llm_config,
    system_message='You are an expert at evaluating if a sentence is sufficiently piratey. It will only be regarded as piratey if it mentions the sea.', #********
    # system_message='If the input sentence is sufficiently piratey, reply AYE THAT\'LL DO. Otherwise, reply MORE PIRATEY, or what needs improving.',
    human_input_mode='NEVER',
    # is_termination_msg=lambda x: x.get('context', '').rstrip().endswith('AYE THAT\'LL DO')
    is_termination_msg=lambda x: x.get('context', '').rstrip().endswith('TERMINATE')
)
evaluator.description = 'Evaluate if an input verse is sufficiently piratey'

exegete = ConversableAgent(
    name='exegete',
    llm_config=llm_config,
    system_message='You are an expert at evaluating if a pirate version of a Bible verse accurately conveys the original intent of the verse. It will only be regarded as conveying the original intent if it contains at least one thou', #******
    # system_message='If the input pirate verse still carries the original verse\'s intent, reply EXCELLENT. Otherwise, reply CONTINUE, or what needs improving.',
    human_input_mode='NEVER',
    # is_termination_msg=lambda x: x.get('context', '').rstrip().endswith('EXCELLENT')
    is_termination_msg=lambda x: x.get('context', '').rstrip().endswith('TERMINATE')
)
exegete.description = 'Evaluate if an input pirate verse still carries the original verse\'s intent'

# verse_saver = ConversableAgent(
#     name='verse_saver',
#     llm_config=llm_config,
#     system_message='You can save a verse to file',
#     human_input_mode='NEVER',
#     code_execution_config={'work_dir': 'web', 'use_docker': False}, # directory to save files to
# )
# verse_saver.description = 'Save a pirate-speak Bible verse to file pirate.txt'


# Can add more assistants here

# allowed_transitions = {
#     team_lead: [translator, evaluator, exegete, verse_saver],
#     translator: [team_lead],
#     evaluator: [team_lead],
#     exegete: [team_lead],
#     verse_saver: [team_lead]
# }

group_chat = GroupChat(
    agents=[translator, evaluator, exegete, team_lead],
    # allowed_or_disallowed_speaker_transitions=allowed_transitions,
    # speaker_transitions_type="allowed",
    messages=[],
    max_round=20,
    send_introductions=True
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config
)

# autogen.register_function(
#     # mixed_verse_generator,
#     pirate_verse_generator,
#     caller=translator,
#     executor=team_lead,
#     # name='mixed_verse_generator',
#     name='pirate_verse_generator',
#     # description='A specialized LLM to generate a new verse based on three incoming verses.'
#     description='A specialized LLM to translate an input Bible verse into pirate-speak'
# )

verses = [
    'By the seventh day God had finished the work he had been doing; so on the seventh day he rested from all his work.',
    'On the seventh day God had finished his work of creation, so he rested from all his work.',
    'By the seventh day God completed His work which He had done, and He rested on the seventh day from all His work which He had done.'
]

verse = 'And God called the firmament Heaven. And the evening and the morning were the second day.'

# Variable of task for agents to complete
# task = f'''
# Combine the following verses into a new verse, and do not provide any additional commentary or explanation in your output:
# {verses[0]},
# {verses[1]},
# {verses[2]},
# '''

task = f'''
Translate this verse into pirate, ensuring it is sufficiently piratey and conveys the original intent. Do not provide any additional commentary or explanation in your output:
{verse}
'''

# Start process
# user_proxy.initiate_chat(
#     translator,
#     message=task
# )

chat_result = team_lead.initiate_chat(
    group_chat_manager,
    message=task,
    summary_method='reflection_with_llm'
)

print(chat_result)