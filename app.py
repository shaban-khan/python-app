from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1> Azure Application Gateway </h1>
    <img src="https://code.benco.io/icon-collection/azure-icons/Application-Gateways.svg" alt="Azure Icon" width="100" height="100">
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
