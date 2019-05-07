from flask import Flask

from ml_api import api

app = Flask(__name__)
app.register_blueprint(api)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
