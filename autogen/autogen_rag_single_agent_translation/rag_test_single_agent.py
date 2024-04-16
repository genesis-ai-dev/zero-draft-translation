import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from dotenv import load_dotenv
import os
import chromadb

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

config_list = [
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

assistant = RetrieveAssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config={
        "timeout": 600,
        "cache_seed": 42,
        "config_list": config_list,
    },
)
ragproxyagent = RetrieveUserProxyAgent(
    name="ragproxyagent",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "task": "qa",
        # "docs_path": [
        #     # "dokumen.pub_a-target-dictionary.pdf",
        
        #     os.path.join(os.path.abspath(""), "dictionary", "english-target.txt"),
        # ],
        "docs_path": [
            os.path.join(os.path.abspath(""), "dictionary", "english-target.txt"),
            os.path.join(os.path.abspath(""), "dictionary", "english-target-dialogs-drills.txt")
            ],  # path to the text file
        "custom_text_types": ["txt"],
        "chunk_token_size": 2000,
        "model": config_list[0]["model"],
        "must_break_at_empty_line": False,
        "client": chromadb.PersistentClient(path="/tmp/chromadb"),
        "embedding_model": "all-mpnet-base-v2",
        "get_or_create": True,  # set to False if you don't want to reuse an existing collection, but you'll need to remove the collection manually
    },
    code_execution_config=False,  # set to False if you don't want to execute the code
)

word_problem = "Translate the following sentence into Target: 'In the beginning, God created the heavens and the earth.'"
ragproxyagent.initiate_chat(
    assistant, 
    message=ragproxyagent.message_generator, 
    problem=word_problem
    # search_string="cognition"
) 