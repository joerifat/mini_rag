from abc import ABC , abstractmethod#Abstract Base Class


class LLMINTERFACE(ABC): #ABC means that this class supposed not to create a direct object from it
    
    

    @abstractmethod
    def set_embedding_model(self,model_id : str,embedding_size: int):

        pass


    @abstractmethod
    def set_generation_model(self, model_id: str):

        pass


    @abstractmethod
    def generate_answer(self,user_prompt: str,chat_history : list=[],max_output_tokens : int=1000,
                        temperature: float =None ):
        pass


    @abstractmethod
    def create_embeddings(self, text: str, document_type: str = None): # document_type(user_prompt,text of file)

        pass



    @abstractmethod
    def construct_prompt(self,prompt:str, role:str):

        pass

    
    