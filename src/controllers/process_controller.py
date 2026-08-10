from .base_controller import BaseController
from .project_controller import ProjectController
from langchain_community.document_loaders import TextLoader,PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from models import ProcessingEnum


class Process_controller(BaseController):

    def __init__(self,project_id : str):
        super().__init__()
        self.project_id = project_id
        self.project_path= ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_id : str):
        return os.path.splitext(file_id)[-1]
    
    def get_file_loader(self, file_id: str):
        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(self.project_path, file_id)

        if not os.path.exists(file_path):
            return None

        if file_ext == ProcessingEnum.Txt.value:
            return TextLoader(file_path, encoding="utf-8")
        
        if file_ext == ProcessingEnum.pdf.value:
            return PyMuPDFLoader(file_path)
        
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    def get_file_content(self, file_id : str):
        
        loader= self.get_file_loader(file_id=file_id)

        if loader:
            return loader.load()
        return None
    
    def process_file_content(self, file_content : list ,  file_id : str , chunk_size: int=100, chunk_overlap: int=20):

        text_splitter=RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap,length_function=len)

        file_content_text=[
            rec.page_content
            for rec in file_content
        ]

        file_content_meta=[
            rec.metadata
            for rec in file_content
        ]

        chunks=text_splitter.create_documents(file_content_text,metadatas=file_content_meta)

        return chunks

        