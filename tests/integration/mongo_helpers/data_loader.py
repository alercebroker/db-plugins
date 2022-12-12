from db_plugins.db.mongo.connection import MongoConnection
from db_plugins.db.mongo.models import Object
import random

random.seed(42)
n_docs = int(1e5)


def object_factory(index):
    stamp_prob = round(random.random(), 5)
    lc_prob = round(random.random(), 5)

    return Object(
        _id="aid{}".format(index),
        aid="aid",
        oid=["oid{}".format(index)],
        tid=["tid{}".format(index)],
        lastmjd=50000.0,
        firstmjd=51000.0,
        meanra=100.0,
        meandec=50.0,
        ndet=2,
        probabilities=[{
            "classifier_name": "stamp_classifier",
            "classifier_version": "stamp_classifier_1.0.0",
            "class_name": "CLASS1",
            "probability": stamp_prob,
            "ranking": 1 if stamp_prob > 0.5 else 2,
        }, {
            "classifier_name": "stamp_classifier",
            "classifier_version": "stamp_classifier_1.0.0",
            "class_name": "CLASS2",
            "probability": 1 - stamp_prob,
            "ranking": 1 if stamp_prob <= 0.5 else 2,
        }, {
            "classifier_name": "lc_classifier",
            "classifier_version": "lc_classifier_1.0.0",
            "class_name": "CLASS1",
            "probability": lc_prob,
            "ranking": 1 if lc_prob > 0.5 else 2,
        }, {
            "classifier_name": "lc_classifier",
            "classifier_version": "lc_classifier_1.0.0",
            "class_name": "CLASS2",
            "probability": 1 - lc_prob,
            "ranking": 1 if lc_prob <= 0.5 else 2,
        }])


def generate_data():
    return [object_factory(i) for i in range(n_docs)]


def load_data(connection: MongoConnection):
    data = generate_data()
    connection.database["object"].insert_many(data, ordered=False)