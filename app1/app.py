from flask import Flask
import logging

app = Flask(__name__)

@app.route('/')
def hello():
    app.logger.info("Serving Azure Application Gateway page")
    return '''
    <h1> Azure Application Gateway 003 </h1>
    <img src="https://code.benco.io/icon-collection/azure-icons/Application-Gateways.svg" alt="Azure Icon" width="100" height="100">
    '''

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000)
