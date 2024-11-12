# API Recommendation (V0.1)

## Description

This project provide an recommendation API to a social network named "Watif" (a student project). There are three implemented recommendation systems :

- 2 with graph exploration and logic (via neo4j database)
- 1 with "embedding" (from / with mongoDB  database)

## Installation

1. Clone this repo :

   ```shell
      git clone <REPO_URI>
      cd <FOLDER_NAME> # The project name by default
   ```
2. Create a virtual env (optional but recommended)  :

   ```shell
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```
3. Installez les dépendances :

   ```shell
   pip install -r requirements.txt
   ```

## Usage

*Don't forget to verify you are in the right folder befor runnig these commands !*

*Don't forget to copy the .env.example file as .env and adapt his content to fit your usage !*

- To run the actual version:

  ```shell
  python -m Recommender [--debug] [--maintenance] [--sync] [--host <host_ip>] [--port <num_port>]
  ```
- To run the actual version (with docker):

  ```shell
   docker build --tag recommandation_api .
   docker run -it --name api recommandation_api
   docker compose up -d
  ```
- To build and install the package:

  ```shell
  # Create a source distribution
  python setup.py sdist

  # Create a wheel distribution
  python setup.py bdist_wheel

  # Install in development mode
  pip install -e .
  ```

## Support

Contact the maintainer of the project for any encounter problems.

## Contributing

This project is open to contributions but subject to conditions.

Suggest changes must have documentation and follow the choosen architecture of the actual project. For deeper changes, refer you to the project owner / maintainer.

## Authors

- Cuisset Mattéo
- Delcambre Jean-Alexis

## License

[MIT License](./LICENSE)
