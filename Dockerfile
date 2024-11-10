# Use an official Python runtime as the base image
FROM python:3.12.7-slim

# Upgrade pip
RUN pip install --upgrade pip

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN useradd -ms /bin/bash nonroot
WORKDIR /home/app
RUN mkdir -p /home/app /var/log/flask-app && \
    chown -R nonroot:nonroot /home/app /var/log/flask-app && \
    touch /var/log/flask-app/flask-app.err.log /var/log/flask-app/flask-app.out.log

USER nonroot

# Copy application files
COPY --chown=nonroot:nonroot ./Recommender ./Recommender
COPY --chown=nonroot:nonroot .env .
COPY --chown=nonroot:nonroot requirements.txt .
COPY --chown=nonroot:nonroot setup.py .

# Set environment variables
ENV FLASK_APP=Recommender/__main__.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production
# venv
ENV VIRTUAL_ENV=/home/app/venv

# Setup Python virtual environment
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Start the application
CMD ["python", "-m", "flask", "run"]
