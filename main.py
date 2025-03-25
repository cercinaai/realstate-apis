# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.apis import api_router
from database import db  # Importer db depuis database.py
from loguru import logger

# Initialiser FastAPI
app = FastAPI(title="RealState API", description="API pour récupérer les annonces et agences", version="1.0.0")

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

@app.on_event("startup")
async def startup_event():
    logger.info("Application démarrée. Connexion à MongoDB établie.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application arrêtée. Connexion à MongoDB fermée.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)