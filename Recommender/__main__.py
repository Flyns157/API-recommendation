"""
This script initializes and runs the RecommendationAPI application, a recommendation service API,
with options for deploying in different modes (debug, maintenance, or deploy) and configurable host
and port settings.

Modules:
    - RecommendationAPI: Provides the main API service for recommendations.
    - argparse: Handles command-line argument parsing.
    - sys: Used for system-specific parameters and error handling.

Functions:
    main(host: str, port: int, mode: str): Initializes and runs the RecommendationAPI with the specified settings.

Command-line Arguments:
    --maintenance: If set, the application runs in maintenance mode.
    --debug: If set, the application runs in debug mode.
    --host: Host IP address on which the application runs. Defaults to '0.0.0.0'.
    --port: Port on which the application listens. Defaults to 8080.
"""

from Recommender import RecommendationAPI
import argparse
import sys

# =================================== Main ===================================
def main(host: str = '0.0.0.0', port: int = 8080, mode: str = 'deploy'):
    """
    Initializes and runs the RecommendationAPI application.

    Args:
        host (str): The IP address to bind the application. Defaults to '0.0.0.0'.
        port (int): The port on which the application listens. Defaults to 8080.
        mode (str): The mode in which to run the application. Options are:
            - 'deploy': Default deployment mode.
            - 'debug': Enables debugging features for development.
            - 'maintenance': Enables maintenance mode, limiting functionality.

    Returns:
        None
    """
    app = RecommendationAPI(__name__,
                            static_url_path='',
                            static_folder='assets',
                            template_folder='templates')
    app.run(mode=mode, host=host, port=port)

# =================================== Run ===================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Python script")
    parser.add_argument('--maintenance', action='store_true', help='Maintenance mode')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host')
    parser.add_argument('--port', type=int, default=8080, help='Port')
    args = parser.parse_args()

    rc = 1  # Return code for script exit status
    try:
        # Determine mode based on command-line arguments and run the application
        main(mode='debug' if args.debug else 'maintenance' if args.maintenance else 'deploy',
             host=args.host,
             port=args.port)
        rc = 0
    except Exception as e:
        print('Error: %s' % e, file=sys.stderr)
    sys.exit(rc)
