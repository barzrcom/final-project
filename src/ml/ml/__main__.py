import json

from flask import Flask
from ml_api import api

app = Flask(__name__)
app.register_blueprint(api)


@app.route("/site_map")
def site_map():
    rules = app.url_map.iter_rules()
    return json.dumps(sorted([str(rule) for rule in rules]))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
