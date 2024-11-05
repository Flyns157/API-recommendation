```
docker build --tag recommandation_api .
docker compose up -d
pip install -r requirements.txt
python -m Recommender
```

```
cls; docker build --tag recommandation_api .
cls; docker run -it --name api recommandation_api
```

To build and install your package:

```
# Create a source distribution
python setup.py sdist

# Create a wheel distribution
python setup.py bdist_wheel

# Install in development mode
pip install -e .
```


For production deployment, you can then:

1. Install using pip from your distribution files
2. Use gunicorn (which is in your requirements.txt) to serve the application:
3. ```
   gunicorn -w 4 'Recommender:RecommendationAPI("Recommender")'
   ```
