# RAG Translation With Multiple Agents  
  
## Overview  
This system utilizes a Retrieval Augmented Generation (RAG) approach to enhance the translation process between English and a target language. The system employs several specialized agents to handle different aspects of the translation task, including data retrieval, translation, editing, and criticism.  
  
## Findings  
During the development and testing phases, it was observed that while the system could produce some translation results, there were limitations due to the large amounts of RAG data being passed from agent to agent. This led to a decision to move towards a more hierarchical, nested structure among the agents to manage data flow and interactions more effectively, thus enhancing system performance and translation quality.  
It was unclear how to incorporate Claude into the RAG agent  
  
## Features  
- **Multiple Specialized Agents**: Includes agents with specific roles such as a researcher, translator, editor, back translator, and critic.  
- **Data Retrieval**: Leverages the RetrieveUserProxyAgent for enhanced content retrieval capabilities.  
- **Hierarchical Agent Interaction**: Uses a structured approach to manage interactions among agents, aiming to streamline the translation process.  
  
## Prerequisites  
- Python 3.x  
- Libraries: `autogen`, `chromadb`, `dotenv`, `os`  
- API access with a valid API key.  
  
## Installation  
Ensure Python 3 and pip are installed on your system. Install the necessary Python libraries:  
```bash  
pip install python-dotenv chromadb  
```  
Follow specific setup instructions for the autogen module as required.  
  
## Setup  
Set up your environment by storing your API key in a .env file:  
```bash  
OPENAI_API_KEY='your_api_key_here'  
ANTHROPIC_API_KEY='your_anthropic_api_key_here'  
```  
## Usage  
Configure the agents with the specific roles and tasks defined in the code.  
Run the script to initiate the translation task where agents collaborate to process the translation from English to the target language.  
Interact with the system through the **`UserProxyAgent`** by providing translation tasks.  
  
## How It Works  
**Data Retrieval:** The **`RetrieveUserProxyAgent`** retrieves relevant documents to aid in translation.  
**Translation Process:** The **`Translator`** agent generates the initial translation which is then reviewed and refined by the **`Editor`**.  
**Quality Assurance:** The **`Back Translator`** and **`Critic`** agents provide feedback and ensure the translation's fidelity and quality.  
  
## Customizing and Extending  
**Agent Configuration:** Modify the agent roles and their tasks to cater to different languages or translation complexities.  
**Data Management:** Adjust retrieval settings and document paths to enhance the context-aware capabilities of the agents.  
  
## Output  
Translated sentences into the target language, along with detailed reports on translation rationale and critiques.  