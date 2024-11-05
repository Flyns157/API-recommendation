# Utiliser une image de base officielle de Python
FROM python:3.12.7-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application dans le conteneur
COPY . /app

# Mettre à jour pip
RUN pip install --upgrade pip

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Configurer la variable d'environnement pour Flask
ENV FLASK_APP=Recommender/__main__.py
ENV FLASK_ENV=production

# Générer une clé secrète pour Flask
RUN python -c 'import secrets; print(secrets.token_hex())' > secret_key.txt
RUN echo "SECRET_KEY=$(cat secret_key.txt)" > .env

# Exposer le port sur lequel l'application va s'exécuter
EXPOSE 8080

# Utiliser un serveur WSGI pour exécuter l'application Flask
CMD ["waitress-serve", "--call", "Recommender.api:create_app"]
