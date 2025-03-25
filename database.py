# database.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

# Charger les variables d'environnement
load_dotenv()

# Récupérer les identifiants et les encoder
username = quote_plus("admin")
password = quote_plus("SuperSecureP@ssw0rd!")
host = os.getenv("MONGO_HOST", "127.0.0.1")  # Par défaut local, à changer pour le serveur
database_name = os.getenv("DATABASE_NAME")

# Construire l'URI MongoDB
mongo_uri = f"mongodb://localhost:27017/xtracto-io-prod"
client = MongoClient(mongo_uri)
db = client[database_name]