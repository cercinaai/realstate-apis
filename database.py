# database.py
import motor.motor_asyncio
from loguru import logger
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer l'URI MongoDB depuis l'environnement
MONGO_URI = os.getenv("MONGO_URI")

# Variables globales pour la connexion
client = None
db = None

async def init_db():
    global client, db
    try:
        if not MONGO_URI:
            raise ValueError("MONGO_URI n'est pas défini dans les variables d'environnement")
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        db = client["xtracto-io-prod"]
        await db.command("ping")  # Vérifie la connexion
        logger.success("✅ Connexion à MongoDB établie")
    except Exception as e:
        logger.critical(f"🚨 Erreur de connexion MongoDB : {e}")
        raise SystemExit(1)

async def close_db():
    global client
    if client:
        client.close()
        logger.info("🔌 Connexion MongoDB fermée")

def get_db():
    if db is None:
        raise RuntimeError("La base de données n'est pas initialisée. Appelez init_db() d'abord.")
    return db