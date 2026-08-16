from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserAuthRequest(BaseModel):
    device_uuid: str
    nickname: str
    is_guest: bool = False

class UserOut(BaseModel):
    id: int
    device_uuid: Optional[str] = None
    nickname: str
    is_guest: bool
    created_at: datetime

    model_config = {"from_attributes": True}
