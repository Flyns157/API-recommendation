from Recommender import RecommendationAPI
import argparse
import sys

# =================================== Main ===================================
def main(host:str='0.0.0.0', port:int=8080, mode:str='deploy'):
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

    rc = 1
    try:
        main(mode='debug' if args.debug else 'maintenance' if args.maintenance else 'deploy', host=args.host, port=args.port, )
        rc = 0
    except Exception as e:
        print('Error: %s' % e, file=sys.stderr)
    sys.exit(rc)
