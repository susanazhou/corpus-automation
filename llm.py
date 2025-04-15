import os
from mistralai import Mistral
from cohere import ClientV2

class LLM: 
    def __init__(self, provider: str, model_name: str):
        self.provider = provider
        self.model_name = model_name

        if self.provider == "mistral":
            self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        elif self.provider == "cohere":
            self.client = ClientV2(api_key=os.getenv("COHERE_API_KEY"))
        else:
            raise ValueError(f"Provider {self.provider} not supported")

    def query_llm(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.0) -> str:
        if self.provider == "mistral":
            response = self.client.chat.complete(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        elif self.provider == "cohere":
            response = self.client.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.message.content[0].text

        else:
            raise ValueError(f"Provider {self.provider} not supported")
        

    def query_structured_llm(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.0, response_format: dict = None) -> str:
        if self.provider == "mistral":
            response = self.client.chat.complete(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format=response_format
            )
            return response.choices[0].message.content
        elif self.provider == "cohere":
            response = self.client.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format=response_format
            )
            return response.message.content[0].text

        else:
            raise ValueError(f"Provider {self.provider} not supported")