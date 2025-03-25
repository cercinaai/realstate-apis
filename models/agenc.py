from pydantic import BaseModel
from typing import Optional

class AgenceOutput(BaseModel):
    id: str
    store_id: str
    name: str
    logo: Optional[str] = None
    intervention_zone: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[str] = None
    phone_number: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None