import json
import os

import pandas as pd
from flask import request, Blueprint
from sklearn.externals import joblib

API_PATH = "/v1/api"

# Create a new 'v1/api' in addition to the APP page
api = Blueprint(API_PATH, __name__)


def available_cities():
    subfolders = [f.name for f in os.scandir('pickles') if f.is_dir()]
    return subfolders


@api.route(f'{API_PATH}/cities', methods=['GET'])
def cities():
    return json.dumps(available_cities(), ensure_ascii=False)


@api.route(f'{API_PATH}/predict', methods=['POST'])
def predict():
    content = request.get_json()

    city = content['city']
    data = content['data']
    algo_name = content.get('algo', 'algo')

    if city not in available_cities():
        # TODO: return error code
        raise ValueError("City is not available.")

    processor = joblib.load(os.path.join("pickles", city, "processor.joblib"))
    algo = joblib.load(os.path.join("pickles", city, f"{algo_name}.joblib"))

    _data = {k: [] for k in data[0].keys()}
    for prop in data:
        for k, v in prop.items():
            _data[k].append(v)

    _X = pd.DataFrame(data=_data)

    _X = processor.transform(_X)
    y_pred = algo.predict(_X)

    return json.dumps(y_pred.tolist())
