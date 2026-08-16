from enum import Enum


class OpenAiEnum(Enum):
    USER="user"
    SYSTEM="system"
    ASSISTANT="assistant"


class CohertEnum(Enum):
    SYSTEM="SYSTEM"
    USER="USER"
    ASSISTANT="CHATBOT"

    #Document
    DOCUMENT="search_document"
    QUERY="search_query"


class LLMFACTORY(Enum):
    OpenAi="openai"
    COHERE="cohere"
    OLLAMA="ollama"

    

