# models/annonce.py
from pydantic import BaseModel
from typing import List, Dict

class AnnonceOutput(BaseModel):
    id: str
    Titre: str
    Description: str
    Prix: float
    Images: List[str]
    L_essentiel: Dict[str, str]
    Bilan_energetique: Dict[str, str]
    Agence: Dict[str, str]
    location: Dict[str, float | str]

    class Config:
        json_encoders = {  # Remplace fields par une configuration valide
            float: lambda v: str(v) if v is not None else None
        }