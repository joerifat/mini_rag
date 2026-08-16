from pydantic import BaseModel
from typing import Optional


class nlp_schema(BaseModel):
    do_rest: Optional[bool]= False

class SearchRequest(BaseModel):
    text: str
    limit: Optional[int] = 5