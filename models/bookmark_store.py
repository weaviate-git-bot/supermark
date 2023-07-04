from typing import List

from pydantic import BaseModel


class UserDoc(BaseModel):
    email: str
    name: str
    folders: List[str]
    subscription_type: str
