#!/usr/bin/env python3

import connexion
from swagger_server import encoder

app = connexion.App(__name__, specification_dir='./swagger/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('swagger.yaml', arguments={'title': 'MNTRK Agent API'}, pythonic_params=True)

def main():
    app.run(port=8081, host='0.0.0.0', debug=True)

if __name__ == '__main__':
    main()
