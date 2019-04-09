import logging

import pandas as pd

from src.crawler.crawler.utils import init_server

logger = logging.getLogger(__name__)


def flat_data(file_content):
    data = list(file_content.values())
    return data


if __name__ == '__main__':
    db, collection = init_server(db_name="yad2_test_1", col="deals")
    res = collection.find()

    columns = []

    doc_properties = []
    for doc in res:
        if not columns:
            columns = doc.keys()
        logger.info(f"reading doc: '{doc}'")

        item = flat_data(doc)
        doc_properties.append(item)

    df = pd.DataFrame(data=doc_properties, columns=columns)
    df.to_csv('data_deals.csv', encoding='utf-8', index=False)
