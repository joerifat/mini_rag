import os


class TemplateParser:

    def __init__(self,language: str, deafult_language:str ="en"):
        self.deafult_language=deafult_language
        self.current_dir=os.path.dirname(os.path.abspath(__file__))

        self.language=self.set_language(language)



    def set_language(self, language:str):
        if not language:
            self.language=self.deafult_language

        language_path=os.path.join(self.current_dir,"locales",language)

        if not os.path.exists(language_path):
            self.language=self.deafult_language

        else:
            self.language=language


    def get(self,group:str , key: str, vars: dict={}):

        if not group or not key:
            return None

        group_path=os.path.join(self.current_dir,"locales",self.language,f"{group}.py")

        if not os.path.exists(group_path):
            return None

        module=__import__(f"stores.llm.templates.locales.{self.language}.{group}",
                          fromlist=[group])

        if not module:
            return None

        key_attribute=getattr(module,key)
        return key_attribute.substitute(vars)


