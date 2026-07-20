from .. import LLMINTERFACE
from .. import llm_enums
import cohere
import logging

class CohereProvider(LLMINTERFACE):

    def __init__(self, api_key: str , deafult_max_input_char: int = 1000,
                 deafult_output_max_tokens:int=1000
                ,deafult_generation_temperature:float=0.1):
        self.api_key=api_key
        self.deafult_max_input_char=deafult_max_input_char
        self.deafult_generation_temperature=deafult_generation_temperature
        self.deafult_output_max_tokens=deafult_output_max_tokens

        self.generation_model_id=None
        self.embedding_model_id=None
        self.embedding_model_size=None

        self.client=cohere.Client(api_key=self.api_key)
        self.logger=logging.Logger(__name__)


    def set_generation_model(self, model_id):
        self.generation_model_id=model_id

    def set_embedding_model(self, model_id, embedding_size):
        self.embedding_model_id=model_id
        self.embedding_model_size=embedding_size


    def process_text(self, text:str ):
        return text[:self.deafult_max_input_char].strip()


    def generate_answer(self, user_prompt, chat_history = [], max_output_tokens = 1000, temperature = None):

        if not self.client:
            self.logger.error("The client is not defined")
            return None

        if not self.generation_model_id:
            return self.logger.error("The generation model is not defined")

        max_output_tokens= max_output_tokens if max_output_tokens else self.deafult_output_max_tokens
        temperature= temperature if temperature else self.deafult_generation_temperature


        response=self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature,
            message=self.process_text(user_prompt)
        )

        if not response or not response.text:
            self.logger.error("Error while generating answer")
            return None

        return response.text


    def create_embeddings(self, text, document_type = None):

        if not self.client:
            self.logger.error("The client of Cohert is not defined")
            return None
        if not self.embedding_model_id:
            self.logger.error("The embdedding model is not defined")

        document_type=llm_enums.CohertEnum.DOCUMENT.value
        if document_type== llm_enums.CohertEnum.QUERY.value:
            document_type=llm_enums.CohertEnum.QUERY.value

        response=self.client.embed(model=self.embedding_model_id,
                                   input_type=document_type,
                                   texts=self.process_text(text),
                                   embedding_types=["float"])

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text")
            return None

        return response.embeddings.float[0]

        
    def construct_prompt(self, prompt, role):
        return {
            "role":role,
            "text":self.process_text(prompt)
        }  


