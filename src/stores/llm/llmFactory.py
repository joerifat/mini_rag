from .llm_enums import LLMFACTORY
from .providers import CohereProvider,OpenAIProvider,OllamProvider
from helpers.config import Settings



class LLMFactory:
    def __init__(self,config: Settings):
        self.config=config

    def create(self,provider: str):
        provider = provider.lower() if provider else ""
        if provider==LLMFACTORY.OpenAi.value:
            return OpenAIProvider(api_key=self.config.OPENAI_APIKEY,
                                  api_url=self.config.OPENAi_URL,
                                  deafult_generation_temperature=self.config.GENERATION_DAFAULT_TEMPERATURE,
                                  deafult_input_max_char=self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                                  deafult_output_max_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS)
        elif provider==LLMFACTORY.COHERE.value:
            return CohereProvider(api_key=self.config.COHERE_APIKEY,
                                  deafult_generation_temperature=self.config.GENERATION_DAFAULT_TEMPERATURE,
                                  deafult_max_input_char=self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                                  deafult_output_max_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS)

        elif provider==LLMFACTORY.OLLAMA.value:
            return OllamProvider(base_url=self.config.BASE_URL)
        return None
        
