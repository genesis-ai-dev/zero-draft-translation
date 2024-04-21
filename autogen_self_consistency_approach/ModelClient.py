import inspect
import json
from typing import Any, Dict, List, Union

from anthropic import Anthropic
from anthropic import __version__ as anthropic_version
from anthropic.types import Completion, Message
from openai.types.chat.chat_completion import ChatCompletionMessage
from typing_extensions import Annotated

import autogen
from autogen import AssistantAgent, UserProxyAgent

TOOL_ENABLED = anthropic_version >= "0.23.1"
if TOOL_ENABLED:
    from anthropic.types.beta.tools import ToolsBetaMessage
else:
    ToolsBetaMessage = object

class AnthropicClient:
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self.model = config["model"]
        anthropic_kwargs = set(inspect.getfullargspec(Anthropic.__init__).kwonlyargs)
        filter_dict = {k: v for k, v in config.items() if k in anthropic_kwargs}
        self._client = Anthropic(**filter_dict)

        self._last_tooluse_status = {}

    def message_retrieval(
        self, response: Union[Message, ToolsBetaMessage]
    ) -> Union[List[str], List[ChatCompletionMessage]]:
        """Retrieve the messages from the response."""
        messages = response.content
        if len(messages) == 0:
            return [None]
        res = []
        if TOOL_ENABLED:
            for choice in messages:
                if choice.type == "tool_use":
                    res.insert(0, self.response_to_openai_message(choice))
                    self._last_tooluse_status["tool_use"] = choice.model_dump()
                else:
                    res.append(choice.text)
                    self._last_tooluse_status["think"] = choice.text

            return res

        else:
            return [  # type: ignore [return-value]
                choice.text if choice.message.function_call is not None else choice.message.content  # type: ignore [union-attr]
                for choice in messages
            ]

    def create(self, params: Dict[str, Any]) -> Completion:
        """Create a completion for a given config.

        Args:
            params: The params for the completion.

        Returns:
            The completion.
        """
        if "tools" in params:
            converted_functions = self.convert_tools_to_functions(params["tools"])
            params["functions"] = params.get("functions", []) + converted_functions

        raw_contents = params["messages"]
        processed_messages = []
        for message in raw_contents:

            if message["role"] == "system":
                params["system"] = message["content"]
            elif message["role"] == "function":
                processed_messages.append(self.return_function_call_result(message["content"]))
            elif "function_call" in message:
                processed_messages.append(self.restore_last_tooluse_status())
            elif message["content"] == "":
                # I'm not sure how to elegantly terminate the conversation, please give me some advice about this.
                message["content"] = "I'm done. Please send TERMINATE"
                processed_messages.append(message)
            else:
                processed_messages.append(message)

        params["messages"] = processed_messages

        if TOOL_ENABLED and "functions" in params:
            completions: Completion = self._client.beta.tools.messages
        else:
            completions: Completion = self._client.messages  # type: ignore [attr-defined]

        # Not yet support stream
        params = params.copy()
        params["stream"] = False
        params.pop("model_client_cls")
        params["max_tokens"] = params.get("max_tokens", 4096)
        if "functions" in params:
            tools_configs = params.pop("functions")
            tools_configs = [self.openai_func_to_anthropic(tool) for tool in tools_configs]
            params["tools"] = tools_configs
        response = completions.create(**params)

        return response

    def cost(self, response: Completion) -> float:
        """Calculate the cost of the response."""
        total = 0.0
        tokens = {
            "input": response.usage.input_tokens if response.usage is not None else 0,
            "output": response.usage.output_tokens if response.usage is not None else 0,
        }
        price_per_million = {
            "input": 15,
            "output": 75,
        }
        for key, value in tokens.items():
            total += value * price_per_million[key] / 1_000_000

        return total

    def response_to_openai_message(self, response) -> ChatCompletionMessage:
        dict_response = response.model_dump()
        return ChatCompletionMessage(
            content=None,
            role="assistant",
            function_call={"name": dict_response["name"], "arguments": json.dumps(dict_response["input"])},
        )

    def restore_last_tooluse_status(self) -> Dict:
        cached_content = []
        if "think" in self._last_tooluse_status:
            cached_content.append({"type": "text", "text": self._last_tooluse_status["think"]})
        cached_content.append(self._last_tooluse_status["tool_use"])
        res = {"role": "assistant", "content": cached_content}
        return res

    def return_function_call_result(self, result: str) -> Dict:
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": self._last_tooluse_status["tool_use"]["id"],
                    "content": result,
                }
            ],
        }

    @staticmethod
    def openai_func_to_anthropic(openai_func: dict) -> dict:
        res = openai_func.copy()
        res["input_schema"] = res.pop("parameters")
        return res

    @staticmethod
    def get_usage(response: Completion) -> Dict:
        return {
            "prompt_tokens": response.usage.input_tokens if response.usage is not None else 0,
            "completion_tokens": response.usage.output_tokens if response.usage is not None else 0,
            "total_tokens": (
                response.usage.input_tokens + response.usage.output_tokens if response.usage is not None else 0
            ),
            "cost": response.cost if hasattr(response, "cost") else 0,
            "model": response.model,
        }

    @staticmethod
    def convert_tools_to_functions(tools: List) -> List:
        functions = []
        for tool in tools:
            if tool.get("type") == "function" and "function" in tool:
                functions.append(tool["function"])

        return functions