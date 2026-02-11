from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class JobCreate(BaseModel):
    type: str = Field(min_length=1, max_length=50)
    payload: Dict[str, Any] = Field(default_factory=dict)
    max_attempts: int = Field(default=3, ge=1, le=10)

class JobOut(BaseModel):
    id: int
    type: str
    payload: Dict[str, Any]
    status: str
    attempts: int
    max_attempts: int
    last_error: Optional[str] = None

    class Config:
        from_attributes = True
