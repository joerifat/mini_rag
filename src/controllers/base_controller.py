# Contain the all the logic needed for all the other controllers

from helpers import get_settings,Settings
import os
import random
import string

class BaseController:
    def __init__(self):
         self.settings = get_settings() #constructor method
         self.base_dir=os.path.dirname(os.path.dirname(__file__))
         self.file_dir= os.path.join(self.base_dir,"assets/files")

    def generate_random_string(self, length: int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

