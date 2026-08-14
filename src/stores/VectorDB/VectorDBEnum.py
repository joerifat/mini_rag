from enum import Enum




class DB(Enum):
    QDRANT="QDRANT"
    PGVetor="PGVECTOR"


class DistanceMethodEnums(Enum):
    COSINE="cosine"
    DOT="dot"

class PGVectorTableschema(Enum):
    ID="id"
    TEXT="text"
    VECTOR="vector"
    METADATA="metadata"
    CHUNK_ID="chunk_id"
    _PREFIX="pgvector"

class PGVectorDistanceMethods(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"

class PGVectorIndexingMethods(Enum):
    HNSW="hnsw"
    IVFFLAT="ivfflat"
    

