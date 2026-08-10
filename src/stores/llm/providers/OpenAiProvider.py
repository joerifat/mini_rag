from ..llm_interface import LLMINTERFACE
from openai import OpenAI
from ..llm_enums import OpenAiEnum
import logging


class OpenAIProvider(LLMINTERFACE):

    def __init__(self,api_key:str,api_url:str =None, 
                   deafult_input_max_char: int=1000,
                   deafult_output_max_tokens:int=1000
                 , deafult_generation_temperature:float=0.1):


        self.api_key=api_key
        self.api_url=api_url
        self.deafult_input_max_char=deafult_input_max_char
        self.deafult_output_max_tokens=deafult_output_max_tokens
        self.deafult_generation_temperature=deafult_generation_temperature


        self.generation_model_id=None
        self.embedding_model_id=None
        self.embedding_size=None
        self.enums=OpenAiEnum

        self.client=OpenAI(
            api_key=self.api_key,
            base_url=self.api_url if self.api_url and len(self.api_url) else None    
        )

        self.logger=logging.getLogger(__name__)


    def set_generation_model(self,model_id):
        self.generation_model_id=model_id

    def set_embedding_model(self, model_id, embedding_size):
        self.embedding_model_id=model_id
        self.embedding_size=embedding_size


    def process_text(self, text: str):
        return text[:self.deafult_input_max_char].strip()


    def generate_answer(self, user_prompt, chat_history = [], max_output_tokens = 1000, temperature = None):

        if not self.client:
            self.logger.error("OpenAi client was not set")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model is not defined")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.deafult_output_max_tokens
        temperature=temperature if temperature else self.deafult_generation_temperature

        chat_history.append(self.construct_prompt(user_prompt,OpenAiEnum.USER.vlaue)) 

        response=self.client.chat.completions.create(model=self.generation_model_id,
                                                     messages=chat_history,
                                                     max_tokens=max_output_tokens,
                                                     temperature=temperature)

        if len(response.choices)==0 or not response.choices[0].message.content or not response or not response.choices:
            self.logger.error("Error while generating text with OpenAI")
            return None

        return response.choices[0].message["content"]


    def create_embeddings(self, text, document_type = None):

        if not self.client:
            self.logger.error("The OpenAi client is not defined")
            return None

        if not self.embedding_model_id:
            self.logger.error("The embedding model is not defined")
            return None

        response=self.client.embeddings.create(model=self.embedding_model_id,
                                               input=text)

        if not response or not response.data or len(response.data)==0 or not response.data[0].embedding:
            self.logger.error("Error while making embeddings")
            return None

        return response.data[0].embedding

           

    def construct_prompt(self, prompt , role):
        return {"role":role,
                "content":self.process_text(prompt)}


        
        
        





