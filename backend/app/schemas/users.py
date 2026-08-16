from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserAuthRequest(BaseModel):
    device_uuid: str
    nickname: str
    password: Optional[str] = Field(None, min_length=4, max_length=20, description="密碼 (4~20 碼)")
    is_guest: bool = False

class UserOut(BaseModel):
    id: int
    device_uuid: Optional[str] = None
    nickname: str
    is_guest: bool
    created_at: datetime

    model_config = {"from_attributes": True}
