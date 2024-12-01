from typing import Any, List, Mapping, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from pydantic import BaseModel, Field
from langchain.llms.base import LLM
from time import sleep
from random import shuffle
import requests
from json import dumps




class APIModel(LLM):

    endpoint: str
    model: str
    key: str
    max_tokens: int
    temperature: float
    system_prompt: str

    @property
    def _llm_type(self) -> str:
        return "evrazGPT"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        
        headers = {
            "Authorization": self.key,
            "Content-Type": "application/json"
        }
        main = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt
                }, 
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        response = requests.post(self.endpoint + "completions",
                                 headers=headers,
                                 json=main
                                 )
        
        if response.status_code == 200:
            answer = response.json().get('choices', [{}])[0].get('message', '').get("content")
            return answer.strip()
        else:
            raise Exception(f"Failed to call APIModel: {response.text}")


    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "endpoint": self.endpoint,
            "model": self.model,
            "key": self.key,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system_prompt": self.system_prompt 
        }


class FakeModel(LLM):
    """
    For testing & debugging
    """

    return_value: bool
    time_sleep: int

    @property
    def _llm_type(self) -> str:
        return "test"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        value = None
        sleep(self.time_sleep)

        if self.return_value:
            value = prompt.split()
            shuffle(value)
            value = " ".join(value)

        return value

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"return_value": self.return_value, "time_sleep": self.time_sleep}
    
    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "evraz"
    
