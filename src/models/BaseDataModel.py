from helpers import get_settings

class BaseDataModel:
    def __init__(self,clientdb : str):
        self.clientdb= clientdb
        self.app_settings=get_settings()