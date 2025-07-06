# Backend Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système nécessaires pour OpenCV et MediaPipe
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements.txt
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Debug : vérifier que le modèle est bien copié
RUN ls -la models_stable_v2/ || echo "Dossier models_stable_v2 introuvable"
RUN ls -la models_stable_v2/best_model_v2.pth || echo "Fichier best_model_v2.pth introuvable"

# Copier le code source
COPY . .

# Démarrer l'application avec uvicorn
CMD ["python", "main.py"]