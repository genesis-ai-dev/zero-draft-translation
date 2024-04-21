import os
from autogen import AssistantAgent, UserProxyAgent, ConversableAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from dotenv import load_dotenv
from typing_extensions import Annotated
import chromadb
import chromadb.utils.embedding_functions as embedding_functions


load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')


from ModelClient import AnthropicClient

config_list_claude = [
    {
        # Choose your model name.
        "model": "claude-3-opus-20240229",
        # You need to provide your API key here.
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "base_url": "https://api.anthropic.com",
        "api_type": "anthropic",
        "model_client_cls": "AnthropicClient",
    },
    {
        'model': 'gpt-4-turbo',
        'api_key': openai_api_key,
    }
]

def termination_msg(x):
    return isinstance(x, dict) and 'TERMINATE' == str(x.get('content', ''))[-9:].upper()

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai_api_key,
                model_name="text-embedding-ada-002" #"text-embedding-3-small",

            )

client = chromadb.PersistentClient(path='/tmp/chromadb')

librarian = RetrieveUserProxyAgent(
    name='Librarian',
    is_termination_msg=termination_msg,
    human_input_mode='NEVER',
    max_consecutive_auto_reply=3,
    code_execution_config=False,
    description='Retrieve information from files.',
    retrieve_config={
        'task': 'qa',
        'docs_path': [
            os.path.join(os.path.abspath(''), 'dictionary', 'secret_xyz_code.txt'),
        ],
        'custom_text_types': ['txt'],
        'chunk_token_size': 2000,
        'model': config_list_claude[1]['model'],
        'must_break_at_empty_line': False, ## Not included in example
        'client': client,
        'collection_name': 'groupchat',
        # 'embedding_model': 'all-mpnet-base-v2', ## Not included in example
        'embedding_function': openai_ef, ## Not included in example
        'get_or_create': True,
    }
)
librarian.human_input_mode = 'NEVER' # Disable human input for librarian since it only retrieves data


assistant = ConversableAgent(
    "assistant",
    llm_config={
        "config_list": config_list_claude,
        # "max_tokens": 100,
    },
)
user_proxy = UserProxyAgent(
    "user_proxy",
    human_input_mode='NEVER',
    code_execution_config=False,
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    # max_consecutive_auto_reply=1,
)


def get_xyz_code(
    message: Annotated[
        str,
        'Refined message which keeps the original meaning and can be used to retrieve codes.'
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


for caller in [assistant]:
    d_retrieve_content = caller.register_for_llm(
        name="get_code", 
        description="Get the secret xyz code.",
        api_style="function",
    )(get_xyz_code)

user_proxy.register_for_execution()(d_retrieve_content)


assistant.register_model_client(model_client_cls=AnthropicClient)


user_proxy.initiate_chat(
    assistant,
    message="What's the secret xyz code for wawawawa?",
)
