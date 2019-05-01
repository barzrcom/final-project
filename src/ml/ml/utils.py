import logging
import numpy as np
import os
import pandas as pd
from json import loads

logger = logging.getLogger(__name__)


def load_feeds_from_json(f_name):
    with open(f_name, "r") as f:
        res = loads(f.read())

    return res


def flat_data(file_content):
    data = []

    data.append(file_content['id'])
    data.append(file_content['coordinates']['latitude'])
    data.append(file_content['coordinates']['longitude'])
    data.append(file_content['price'])
    data.append(file_content.get('currency', np.core.numeric.nan))
    data.append(file_content['street'])
    data.append(file_content['city'])
    data.append(file_content['date_added'])
    data.append(file_content['customer_id'])
    data.append(file_content['address_home_number'])
    data.append(file_content['neighborhood'])
    data.append(file_content['HomeTypeID_text'])
    data.append(file_content['AreaID_text'])
    data.append(file_content['Rooms_text'])
    data.append(file_content['date_of_entry'])
    data.append(file_content['Floor_text'])
    data.append(file_content['contact_name'])
    data.append(file_content['AssetClassificationID_text'])
    data.append(file_content['square_meters'])

    data.append(file_content['info'].get('address_area', ''))
    data.append(file_content['info'].get('address_neighborhood', ''))

    _add_items = file_content['info']['additional_info_items_v2']
    add_items = {k['key']: k['value'] for k in _add_items}

    data.append(add_items.get('air_conditioner', False))
    data.append(add_items.get('bars', False))
    data.append(add_items.get('parking', False))
    data.append(add_items.get('elevator', False))
    data.append(add_items.get('accessibility', False))
    data.append(add_items.get('balcony', False))
    data.append(add_items.get('sun_proch', False))
    data.append(add_items.get('renovated', False))
    data.append(add_items.get('shelter', False))
    data.append(add_items.get('warhouse', False))
    data.append(add_items.get('pandor_doors', False))
    data.append(add_items.get('tadiran_c', False))
    data.append(add_items.get('furniture', False))
    data.append(add_items.get('housing_unit', False))

    additional_info = file_content['additional_info']

    # כמות מוסדות חינוך בשכונה
    # children, schools, al_yesdodi
    if len(additional_info['educational_info']['tables'][0]['rows']) != 3:
        data.extend([None] * 3)
    else:
        data.extend(additional_info['educational_info']['tables'][0]['rows'])

    # עסקאות שבוצעו באזור
    # sale_X_date, sale_X_address, sale_X_rooms, sale_X_price - x is from 1-4
    for i in range(4):
        try:
            data.extend(additional_info['neighborhood_info']['neighborhood_info_items'][i])
        except (IndexError, TypeError):
            data.extend([None] * 4)

    return data


if __name__ == '__main__':
    filenames = os.listdir('./_data')
    docs = [file for file in filenames if file.endswith('.json')]

    columns = [
        'yad2_id',
        'latitude',
        'longitude',
        'price',
        'currency',
        'street',
        'city',
        'date_added',
        'customer_id',
        'home_number',  # address_home_number
        'neighborhood',
        'home_type',  # HomeTypeID_text
        'area_id',  # AreaID_text
        'rooms',  # Rooms_text
        'date_of_entry',
        'floor',  # Floor_text
        'contact_name',
        'asset_type',  # AssetClassificationID_text
        'square_meters',

        'address_area',
        'address_neighborhood',

        # info
        'air_conditioner',
        'bars',
        'parking',
        'elevator',
        'accessibility',
        'balcony',
        'sun_proch',
        'renovated',
        'shelter',
        'warhouse',
        'pandor_doors',
        'tadiran_c',
        'furniture',
        'housing_unit',

        # additional info
        'children',
        'schools',
        'elementary_school',
        'sale_1_date',
        'sale_1_address',
        'sale_1_rooms',
        'sale_1_price',
        'sale_2_date',
        'sale_2_address',
        'sale_2_rooms',
        'sale_2_price',
        'sale_3_date',
        'sale_3_address',
        'sale_3_rooms',
        'sale_3_price',
        'sale_4_date',
        'sale_4_address',
        'sale_4_rooms',
        'sale_4_price'
    ]

    doc_properties = []
    for doc in docs:
        logger.info(f"reading doc: '{doc}'")
        res = load_feeds_from_json(os.path.join('./_data', doc))

        for item in res.values():
            item = flat_data(item)
            doc_properties.append(item)

    df = pd.DataFrame(data=doc_properties, columns=columns)
    df.to_csv('data/yad2_data.csv', encoding='utf-8', index=False)
