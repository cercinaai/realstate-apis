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
host = os.getenv("MONGO_HOST", "127.0.0.1")  # Par défaut local
database_name = os.getenv("DATABASE_NAME", "xtracto-io-prod")

# Construire l'URI MongoDB
mongo_uri = f"mongodb://{username}:{password}@{host}:27017/{database_name}?authSource=admin"
client = MongoClient(mongo_uri)
db = client[database_name]