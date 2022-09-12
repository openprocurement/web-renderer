import argparse
from waitress import serve

from app import app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Host and port configuration')
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=8080)
    args = parser.parse_args()
    serve(app, host=args.host, port=args.port)
