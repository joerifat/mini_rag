from ..llm_interface import LLMINTERFACE
from helpers.config import get_settings
from ollama import Client




class OllamProvider(LLMINTERFACE):
    def __init__(self,base_url:str):

        self.client=Client(host=base_url)
        self.embedding_model_id=None
        self.generation_model_id=None
        self.embedding_model_size=None
        self.settings=get_settings()




    def set_embedding_model(self, model_id, embedding_size):
        self.embedding_model_id=model_id
        self.embedding_model_size=embedding_size


    def set_generation_model(self, model_id):
        self.generation_model_id=model_id



    def construct_prompt(self, prompt, role):
        return {
            "role":role,
            "content":prompt
        }


    def create_embeddings(self, text, document_type = None):
        if not self.embedding_model_id:
            raise ValueError("The embedding model is not defined")

        response=self.client.embed(model=self.embedding_model_id,
                                   input=text)


        embedding=response["embeddings"]

        if self.embedding_model_size is not None:
            if len(embedding) != self.embedding_model_size:
                 raise ValueError(
                    f"Embedding dimension mismatch: "
                    f"expected {self.embedding_size}, "
                    f"received {len(embedding)}"
                )
        return embedding


    def generate_answer(self, user_prompt, chat_history = [], max_output_tokens = 1000, temperature = None):
        if not self.generation_model_id:
            raise ValueError("The generation model is not defined")


        messages=[]
        messages=chat_history.copy()

        messages.append(
            self.construct_prompt(
                prompt=user_prompt,
                role="user"
            )
        )

        options = {
            "num_predict": max_output_tokens
        }

        if temperature is not None:
            options["temperature"] = temperature

   

        response=self.client.chat(model=self.generation_model_id,messages=messages,options=options)

        return response["message"]["content"]