# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.apis import api_router
from database import db
from loguru import logger
from contextlib import asynccontextmanager
from database import init_db, close_db 
# Gestionnaire de lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # <-- Manquait cet appel
    logger.info("✅ Application démarrée. Connexion à MongoDB établie.")
    yield
    await close_db()
    logger.info("🛑 Application arrêtée. Connexion à MongoDB fermée.")

# Initialiser FastAPI avec lifespan
app = FastAPI(
    title="RealState API",
    description="API pour récupérer les annonces et agences",
    version="1.0.0",
    lifespan=lifespan
)

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes API
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5009)