# Pirate Speak Bible Verse Translator  
  
## Overview  
This program translates Bible verses into pirate speak, ensuring the translation retains the original intent of the text while incorporating a piratey tone. It uses a conversational agent framework with multiple agents specializing in translation, evaluation, and adherence to the original intent.  
  
## Findings  
The agents effectively made the Bible verses sound more piratey, while it occassionally even rubbed off on them:  
```  
--------------------------------------------------------------------------------  
translator (to chat_manager):  
translator, please translate the verse into pirate speak.  
--------------------------------------------------------------------------------  
translator (to chat_manager):  
Arr, the Almighty named the sky 'Heaven'. The dusk and dawn marked the second day, says I.  
--------------------------------------------------------------------------------  
evaluator (to chat_manager):  
That's a fine piratey translation, matey. It's got the right amount of sea dog lingo and keeps to the original meaning.  
--------------------------------------------------------------------------------  
exegete (to chat_manager):  
Great! Now, exegete, please evaluate if this pirate translation still carries the original verse's intent.  
--------------------------------------------------------------------------------  
exegete (to chat_manager):  
Aye, the translation be keepin' true to the original intent. The Almighty's naming of the sky as 'Heaven' and the marking of the second day by dusk and dawn be clearly conveyed.  
```  
  
## Features  
- **Pirate Translation**: Converts Bible verses into pirate speak.  
- **Evaluation System**: Agents to evaluate the "pirateyness" and fidelity to the original text.  
- **Automated Conversational Agents**: Utilize a series of conversational agents that collaborate to refine translations.  
  
## Prerequisites  
- Python 3.x  
- Libraries: `autogen`, `dotenv`, `os`  
- Environmental variables for API configuration.  
  
## Installation  
Ensure Python 3 and pip are installed on your system. Install the necessary libraries:  
```bash  
pip install python-dotenv pyautogen  
```  
  
## Setup  
Set up your environment by storing your OpenAI API key in a .env file:  
```bash  
OPENAI_API_KEY='your_api_key_here'  
```  
  
## Usage  
1. Configure the environment variables to match your setup requirements.  
2. Run **`app.py`** to initiate the translation process.  
3. Interact with the conversational agents as they collaboratively translate and evaluate verses.  
  
## How It Works  
- **Translation Initiation:** Begins with a predefined Bible verse to be translated into pirate speak.  
- **Agent Interaction:** Multiple agents, including a translator, evaluator, and exegete, interact within a group chat setting to refine the translation.  
- **Agent Roles:**  
  - **Translator:** Translates the Bible verse into pirate speak.  
  - **Evaluator:** Ensures the translation meets the criteria for "pirateyness".  
  - **Exegete:** Confirms the translation preserves the original intent of the verse.  
  
## Customizing and Extending  
- **Modifying Agents:** Agents can be customized or extended to include more complex behaviors or additional evaluation criteria.  
- **Adding New Agents:** Introduce new roles or responsibilities within the translation process.  
  
## Output  
- Translated verses in pirate speak, along with evaluations on their quality and fidelity.  
  
## Example Usage  
The program can be executed to translate specific verses provided in the script, or modified to accept input dynamically from users.  
  
