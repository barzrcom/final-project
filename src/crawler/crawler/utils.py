import logging
from bson.json_util import loads
from pymongo import MongoClient

logger = logging.getLogger(__name__)


def init_server(db_name, col):
    client = MongoClient()
    db = client[db_name]
    collection = db[col]
    return db, collection


def load_feeds_from_json(f_name):
    with open(f_name, "r") as f:
        res = loads(f.read())

    return res


if __name__ == '__main__':
    db, collection = init_server(db_name="yad2_test_1", col="col1")
    num_of_files = 62

    docs = [
        "feeds_{}.json".format(i) for i in range(1, num_of_files)
    ]

    for doc in docs:
        logger.info(f"writing doc to DB, doc name: {doc}")
        res = load_feeds_from_json(doc)

        for item in res.values():
            collection.insert(item)
