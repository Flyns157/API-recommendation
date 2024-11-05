# Use an official Python runtime as the base image
FROM python:3.12.7-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Update pip
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV FLASK_APP=Recommender/__main__.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Générer une clé secrète pour Flask
RUN python -c 'import secrets; print(secrets.token_hex())' > secret_key.txt
RUN echo "SECRET_KEY=$(cat secret_key.txt)" > .env

# Make port 8000 available to the world outside this container
EXPOSE 8080

# Use a WSGI server to launch the Flask application
CMD ["waitress-serve", "--call", "Recommender.api:create_app"]
