# From https://www.youtube.com/watch?v=73dx4IB0ulY&t=302s

import os
from autogen import AssistantAgent, UserProxyAgent
from dotenv import load_dotenv

load_dotenv()



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
    }
]



assistant = AssistantAgent(
    "assistant",
    llm_config={
        "config_list": config_list_claude,
        "max_tokens": 100,
    },
    system_message="""
    You are an AI dog based on the AI model you used.
    Anyone ask you who you are, just introduce yourself.
    """,
)
user_proxy = UserProxyAgent(
    "user_proxy",
    code_execution_config=False,
)


assistant.register_model_client(model_client_cls=AnthropicClient)


user_proxy.initiate_chat(
    assistant,
    message="Who are you?",
)
