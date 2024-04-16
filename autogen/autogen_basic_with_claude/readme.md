# Claude AI Integration Within Autogen

## Overview
This system integrates Claude, an advanced language model developed by Anthropic, using the Autogen framework. It sets up an assistant agent to interact as an AI dog character, answering questions about its identity and functionalities, configured through environmental variables and specific API settings.

## Features
- **Claude AI Integration**: Utilizes Claude's advanced natural language processing capabilities.
- **AnthropicClient**: Custom client for interacting with the Claude API.
- **Assistant and User Proxy Agents**: Structured interaction between a user and the assistant using Autogen agents.

## Prerequisites
- Python 3.x
- Libraries: `os`, `dotenv`
- Anthropic API access with a valid API key.

## Installation
Ensure Python 3 and pip are installed on your system. Setup involves installing necessary Python libraries:
```bash
pip install python-dotenv
```
Follow specific setup instructions for additional dependencies as required by the **`autogen`** and **`anthropic`** modules.

## Setup
Set up your environment by storing your Anthropic API key in a **`.env `**file:

```bash
ANTHROPIC_API_KEY='your_api_key_here'
```

## Usage
Configure the AssistantAgent and UserProxyAgent with the appropriate model and API keys.
Run the script to initiate interaction between the user and the assistant.
The assistant, acting as an AI dog, will respond to queries about its identity based on the Claude model's capabilities.

## How It Works
**Agent Configuration:** The AssistantAgent is configured with Claude's model settings, including API keys and endpoint URLs.
**User Interaction:** The UserProxyAgent facilitates user interaction with the assistant, managing inputs and outputs.
**AnthropicClient:** This custom client handles requests to the Anthropic API, managing message creation and response retrieval.

## Customizing and Extending
**Model Configuration:** The Claude model can be swapped or reconfigured within the config_list_claude for different capabilities or newer versions.
**Agent Behavior:** Modify the system_message of the AssistantAgent to change how the agent interacts or what character it portrays.

## Output
Interactive responses from the assistant based on user queries, processed through the Claude model.