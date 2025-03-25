# Utiliser l'image officielle Python 3.12.8 slim comme base
FROM python:3.12.8-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances sans cache pour réduire la taille de l'image
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source dans le conteneur
COPY . .

# Exposer le port 5000 (ou 5001 si vous avez modifié main.py)
EXPOSE 5009

# Commande pour démarrer l'application
CMD ["python", "main.py"]