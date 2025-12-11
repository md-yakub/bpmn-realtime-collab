from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

"""
Pydantic models describing the WebSocket message protocol used by the
ConnectionManager. These schemas are primarily used in tests and debugging
to validate the structure of messages emitted by the backend during
real-time collaboration.
"""

class User(BaseModel):
    id: str
    name: str


class BaseMessage(BaseModel):
    type: str

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True
    )


class InitStateMessage(BaseMessage):
    type: str = "init_state"
    xml: str
    revision: int
    users: List[User]
    locks: Dict[str, str]


class UsersMessage(BaseMessage):
    type: str = "users"
    users: List[User]


class BpmnUpdateMessage(BaseMessage):
    type: str = "bpmn_update"
    xml: str
    revision: int
    from_user: Optional[str] = Field(default=None, alias="from")


class LockMessage(BaseMessage):
    type: str = "lock"
    elementId: str
    userId: str


class UnlockMessage(BaseMessage):
    type: str = "unlock"
    elementId: str
    userId: str

class LocksSyncMessage(BaseModel):
    type: Literal["locks"]
    locks: Dict[str, str]
