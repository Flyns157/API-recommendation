"""
This is the main module of the Recommender package.
It contains the main() function, which is the entry point of the program.
The main() function creates a RecommenderFastAPI instance and runs it with Uvicorn.
"""
import sys
from . import RecommenderFastAPI
import argparse
import uvicorn

# =================================== Main ===================================
def main(debug=False, host='127.0.0.1', port=8080):
    app = RecommenderFastAPI(debug=debug, host=host, port=port)
    # Run the FastAPI app with Uvicorn
    uvicorn.run(app, host=host, port=port, log_level="debug" if debug else "info")

# =================================== Run ===================================
if __name__ == '__main__':
    """
    Parse command-line arguments and start the Flask application.

    The script supports the following command-line arguments:
    - --debug: Run the application in debug mode.
    - --host: The hostname to listen on (default: '0.0.0.0').
    - --port: The port of the web server (default: 8080).
    """
    parser = argparse.ArgumentParser(description="Recommender API - entry point")
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host')
    parser.add_argument('--port', type=int, default=8080, help='Port')
    args = parser.parse_args()

    rc = 1
    try:
        main(debug=args.debug, host=args.host, port=args.port)
        rc = 0
    except Exception as e:
        print('Error: %s' % e, file=sys.stderr)
    sys.exit(rc)
