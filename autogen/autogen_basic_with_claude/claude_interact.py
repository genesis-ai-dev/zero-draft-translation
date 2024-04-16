import anthropic
import os
from dotenv import load_dotenv
load_dotenv()

message = r"""
Message to Claude goes here.
"""

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv('ANTHROPIC_API_KEY'),
)

message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    temperature=0.0,
    system="YOu are an expert in python, autogen, and api usage.",
    messages=[
        {
            "role": "user", 
            "content": message
        }
    ]
)

print(message.content)