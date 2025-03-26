from pydantic import BaseModel
from typing import Optional

class AgenceModel(BaseModel):
    storeId: str
    name: str
    lien: Optional[str] = None
    CodeSiren: Optional[str] = None
    logo: Optional[str] = None
    adresse: Optional[str] = None
    zone_intervention: Optional[str] = None
    siteWeb: Optional[str] = None
    horaires: Optional[str] = None
    number: Optional[str] = None
    description: Optional[str] = None
    scraped_at: Optional[str] = None
    email: Optional[str] = None

    class Config:
        extra = "ignore"

class AgencyUpdate(BaseModel):
    email: Optional[str] = None
    number: Optional[str] = None

    class Config:
        extra = "ignore"