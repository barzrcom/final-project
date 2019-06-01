import logging
from bson.json_util import loads
from pymongo import MongoClient

logger = logging.getLogger(__name__)


def init_server(db_name, col):
    client = MongoClient(socketTimeoutMS=20000, waitQueueTimeoutMS=20000)
    db = client[db_name]
    collection = db[col]
    return db, collection


def load_feeds_from_json(f_name):
    with open(f_name, "r") as f:
        try:
            res = loads(f.read())
        except UnicodeDecodeError as e:
            print(f.read())
            return None

    return res


if __name__ == '__main__':
    db, collection = init_server(db_name="yad2_test_1", col="col1")
    num_of_files = 56

    docs = [
        "feeds_{}.json".format(i) for i in range(1, num_of_files)
    ]

    for doc in docs:
        print(f"writing doc to DB, doc name: {doc}")
        res = load_feeds_from_json(doc)
        if res is None:
            continue

        for item in res.values():
            collection.insert(item)
