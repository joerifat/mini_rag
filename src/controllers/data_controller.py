# Contain all the logic needed for file ingestion

from fastapi import UploadFile
from .base_controller import BaseController
from models import UserResponses
from .project_controller import ProjectController
import os
import re

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.scale=1048576 # convert MB to bytes

    def validate(self, file: UploadFile):
        # Validate the file type
        if file.content_type not in self.settings.FILE_TYPE_AVAILABLE:
            return False,UserResponses.FILE_TYPE_NOT_SUPPORTED.value 
        elif file.size > self.settings.FILE_SIZE_LIMIT*self.scale:
            return False,UserResponses.FILE_SIZE_EXCEEDED.value
        else:
            return True,UserResponses.FILE_VALIDATED_SUCCESS.value
        

    def generate_unique_file_name(self, origin_file_name : str, project_id : str):

        random_filename= self.generate_random_string()
        project_path= ProjectController().get_project_path(project_id)

        cleaned_file_name = self.get_clean_file_name(
            orig_file_name=origin_file_name
        )

        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_file_name
        )

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_file_name
            )

        return new_file_path, random_key + "_" + cleaned_file_name

    def get_clean_file_name(self, orig_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name


         
