from pydantic import BaseModel
from typing import Optional

class PushRequest(BaseModel):
    do_rest:Optional[bool]=False