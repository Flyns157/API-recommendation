FROM python:3.12.7-slim

WORKDIR /app/

RUN python -m venv .venv

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./Recommender /app/app

EXPOSE 8080

CMD ["fastapi", "run", "--workers", "4", "app"]
