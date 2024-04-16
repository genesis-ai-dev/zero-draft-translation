# Retrieval Augmented Translation Assistant  
  
## Overview  
This system enhances the translation process by using a Retrieval Augmented Generation (RAG) approach, where the agent retrieves relevant information to assist in translating sentences into the target language. It leverages the capabilities of `chromadb` for persistent data storage and retrieval, combined with a powerful language model for generation.  
**Note:** When clearing the cache, remove any relevant files created in the **`tmp/chromadb`** folder  
  
## Findings  
After feedback from the target language community, single-prompt responses from Claude yielded more accurate results.  
  
## Features  
- **Contextual Data Retrieval**: Retrieves relevant information from a structured database to assist in translation.  
- **RAG Agents**: Uses `RetrieveAssistantAgent` and `RetrieveUserProxyAgent` from Autogen to handle user queries and generate responses.  
- **Customizable Data Sources**: Includes the flexibility to specify document paths for retrieval, enhancing the context-aware capabilities of the agent.  
  
## Prerequisites  
- Python 3.x  
- Libraries: `autogen`, `chromadb`, `dotenv`, `os`  
- API access with a valid API key.  
  
## Installation  
Ensure Python 3 and pip are installed on your system. Install the necessary Python libraries:  
```bash  
pip install python-dotenv chromadb pyautogen  
```  
  
## Setup  
Set up your environment by storing your API key in a **`.env`** file:  
```bash  
OPENAI_API_KEY='your_api_key_here'  
```  
  
## Usage  
Configure the document paths in retrieve_config to include files relevant to the translation task.  
Run the script to initiate the RAG process, where the system retrieves information and uses it to assist in generating translations.  
Interact with the system through the RetrieveUserProxyAgent by providing translation tasks.  
## How It Works  
**Document Setup:** Document paths are configured to point to the necessary textual resources which contain information relevant to the target language.  
**Data Retrieval:** chromadb is used to manage and retrieve data, making the translation process more informed and accurate.  
**Translation Generation:** The RetrieveAssistantAgent uses the retrieved information along with a language model to generate translations that are contextually enriched.  
  
## Customizing and Extending  
**Data Sources:** Adjust the document paths and the types of documents considered to refine the contextual information available for retrieval.  
**Agent Configuration:** Modify the system messages and retrieval configurations to change how the agents interact or to adapt to different translation scenarios.  
## Output  
Translated sentences into the target language, informed by retrieved data that enhances the translation's accuracy and contextual relevance.  