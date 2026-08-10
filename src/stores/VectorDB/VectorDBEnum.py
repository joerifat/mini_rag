from enum import Enum




class Qdrantdb(Enum):
    QDRANT="QDRANT"


class DistanceMethodEnums(Enum):
    COSINE="cosine"
    DOT="dot"
