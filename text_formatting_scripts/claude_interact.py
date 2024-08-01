import anthropic
import os
from pypdf import PdfReader
from dotenv import load_dotenv
load_dotenv()


# number_of_pages = len(reader.pages)
# text = ''.join(page.extract_text() for page in reader.pages)
# print(text[:2155])


message = """Translate the following into Tamazight with Arabic script (NOT Tifinagh): \"
    He shall bring his trespass offering to the LORD: a ram without defect from the flock, according to your estimation, for a trespass offering, to the priest.
    """

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv('ANTHROPIC_API_KEY'),
)



message = client.messages.create(
    model="claude-3-opus-20240229",
    # model='claude-3-haiku-20240307',
    max_tokens=4096,
    temperature=0.0,
    system=f"You are an expert at translating from English into Tamazight with Arabic script.",
    messages=[
        {
            "role": "user", 
            "content": message
        }
    ]
)

print(message.content[0].text)