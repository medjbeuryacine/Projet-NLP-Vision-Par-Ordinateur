# Frontend Dockerfile
FROM node:20-alpine

# Installer ffmpeg pour le traitement vidéo
RUN apk add --no-cache ffmpeg

WORKDIR /usr/src/app

# Copier package.json et package-lock.json
COPY package.json package-lock.json ./

# Installer les dépendances
RUN npm install --legacy-peer-deps

# Copier le code source
COPY . .

# Exposer le port Vite
EXPOSE 5173

# Démarrer Vite avec host pour Docker
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]