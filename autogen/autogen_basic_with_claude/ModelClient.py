import inspect
from typing import Any, Dict, List, Union

from anthropic import Anthropic
from anthropic.types import Completion, Message

import autogen
from autogen import AssistantAgent, UserProxyAgent
from autogen.oai.openai_utils import OAI_PRICE1K

class AnthropicClient:
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self.model = config["model"]
        anthropic_kwargs = set(inspect.getfullargspec(Anthropic.__init__).kwonlyargs)
        filter_dict = {k: v for k, v in config.items() if k in anthropic_kwargs}
        self._client = Anthropic(**filter_dict)

    def message_retrieval(self, response: Message) -> Union[List[str], List]:
        """Retrieve the messages from the response."""
        choices = response.content
        if isinstance(response, Message):
            return [choice.text for choice in choices]  # type: ignore [union-attr]

        # claude python SDK and API not yet support function calls

    def create(self, params: Dict[str, Any]) -> Completion:
        """Create a completion for a given config using openai's client.

        Args:
            client: The openai client.
            params: The params for the completion.

        Returns:
            The completion.
        """
        if "messages" in params:
            raw_contents = params["messages"]
            if raw_contents[0]["role"] == "system":
                system_message = raw_contents[0]["content"]
                raw_contents = raw_contents[1:]
                params["messages"] = raw_contents
                params["system"] = system_message
                # params["max_tokens"] = 4000 #added this line
                # params["model"] = self.model #added this line
            completions: Completion = self._client.messages  # type: ignore [attr-defined]
        else:
            completions: Completion = self._client.completions

        # Not yet support stream
        params = params.copy()
        params["stream"] = False
        params.pop("model_client_cls")
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
    


