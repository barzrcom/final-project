import codecs
import json
import os

import pandas as pd
from flask import request, Blueprint
from sklearn.externals import joblib

API_PATH = "/api/ml/v1"

# Create a new 'v1/api' in addition to the APP page
api = Blueprint(API_PATH, __name__)


def _available_cities():
    subfolders = [f.name for f in os.scandir('pickles') if f.is_dir()]
    return subfolders


def _city_values(city):
    # check for cache
    json_f = os.path.join("pickles", city, "streets.json")
    if not os.path.exists(json_f):
        # TODO: cache should be FileSystemCache to be limited to time and not by existent of file
        df = pd.read_csv("data/map_address_neighborhood.csv")
        df = df.loc[city == df['city']]

        content = json.dumps({
            "street": df['street'].drop_duplicates().sort_values().get_values().tolist(),
            "neighborhood": df['neighborhood'].drop_duplicates().sort_values().get_values().tolist()
        }, ensure_ascii=False)
        with codecs.open(json_f, 'wb', encoding='utf-8') as f:
            f.write(content)

    with open(json_f, 'r', encoding='utf-8') as f:
        content = json.load(f)

    return content


@api.route(f'{API_PATH}/cities', methods=['GET'])
def cities():
    return json.dumps(_available_cities(), ensure_ascii=False)


@api.route(f'{API_PATH}/neighborhoods/<city>', methods=['GET'])
def neighborhood(city):
    if city not in _available_cities():
        return f"City '{city}'' is not available.", 404

    content = _city_values(city)
    return json.dumps(content['neighborhood'], ensure_ascii=False)


@api.route(f'{API_PATH}/streets/<city>', methods=['GET'])
def streets(city):
    if city not in _available_cities():
        return f"City '{city}'' is not available.", 404

    content = _city_values(city)
    return json.dumps(content['street'], ensure_ascii=False)


@api.route(f'{API_PATH}/property_types', methods=['GET'])
def property_types():
    # TODO: should be dynamically from data
    # df['property_type'].unique().tolist()
    types = ['דירה בבית קומות', 'דירת גג', 'דירת מגורים', 'בית בודד',
             "קוטג' חד משפחתי", "קוטג' דו משפחתי", 'דירת נופש', 'דירת גן']
    return json.dumps(types, ensure_ascii=False)


@api.route(f'{API_PATH}/build_years', methods=['GET'])
def build_years():
    # TODO: should be dynamically from data
    # import time
    # vals = df['build_year'].unique().astype(int).tolist()
    #
    # years = []
    # for v in vals:
    #     z = time.strftime("%Y", time.gmtime(v/1000000000))
    #     years.append(z)
    # years = sorted(years)
    # print(f"From year: {years[0]}, to year: {years[-1]}")
    return json.dumps(list(range(1945, 2023)))  # statically from 1945 - 2022


@api.route(f'{API_PATH}/predict', methods=['POST'])
def predict():
    content = request.get_json()
    print(content)
    city = content['city']
    data = content['data']
    algo_name = content.get('algo', 'algo')

    if city not in _available_cities():
        return f"City '{city}'' is not available.", 404

    processor = joblib.load(os.path.join("pickles", city, "processor.joblib"))
    algo = joblib.load(os.path.join("pickles", city, f"{algo_name}.joblib"))

    _data = {k: [] for k in data[0].keys()}
    for prop in data:
        for k, v in prop.items():
            # "rooms_number": 4,
            # "floor": 10,
            # "building_mr": 116,
            # "build_year": "2019-01-01",
            v['rooms_number'] = int(v['rooms_number'])
            v['floor'] = int(v['floor'])
            v['building_mr'] = int(v['building_mr'])
            v['build_year'] = f"{v['build_year']}-01-01"
            _data[k].append(v)

    _X = pd.DataFrame(data=_data)

    _X = processor.transform(_X)
    y_pred = algo.predict(_X)

    return json.dumps(y_pred.tolist())
