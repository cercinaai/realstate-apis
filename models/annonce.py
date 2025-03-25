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
        fields = {
            "L_essentiel": "L'essentiel",
            "Bilan_energetique": "Bilan énergétique"
        }