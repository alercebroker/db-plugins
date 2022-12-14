from db_plugins.db.mongo.connection import MongoConnection
from db_plugins.db.mongo.models import Object
import random

random.seed(42)
classifiers = {  # mapping of classifier name to number of classes in said classifier
        "stamp_classifier": 5,
        "lc_classifier": 15,
        "lc_classifier_top": 3,
        "lc_classifier_transient": 4,
        "lc_classifier_stochastic": 5,
        "lc_classifier_variable": 6
    }
n_features = 150


def object_factory(index):
    aid = f"aid{index}"

    return Object(
        _id=aid,
        aid=aid,
        oid=["oid{}".format(index)],
        tid=["tid{}".format(index)],
        lastmjd=50000.0,
        firstmjd=51000.0,
        meanra=100.0,
        meandec=50.0,
        ndet=2,
        probabilities=generate_probabilities(),
        # features=generate_features(n_features)  # There's not much to do with features for now
    )


def generate_probabilities():
    taxonomy = {name: [f"CLASS{i + 1}" for i in range(n_class)] for name, n_class in classifiers.items()}

    generated_probabilities = []

    for classifier, classes in taxonomy.items():
        random.shuffle(classes)
        class_probs = []
        for i in range(len(classes)):
            off = 0 if i == 0 else sum(class_probs)
            class_probs.append(1 - off if i == len(classes) - 1 else random.random() * (1 - off))
        class_probs.sort(reverse=True)

        generated_probabilities.extend(
            [
                probability_factory(classifier, class_name, class_probs[rank], rank + 1)
                for rank, class_name in enumerate(classes)
            ]
        )

    return generated_probabilities


def probability_factory(classifier_name, class_name, prob, rank):
    return {
        "classifier_name": classifier_name,
        "classifier_version": f"{classifier_name}_1.0.0",
        "class_name": class_name,
        "probability": prob,
        "ranking": rank,
    }


def generate_features(nfeatures):
    return [feature_factory("name", 1.0, 1, "1.0.0") for _ in range(nfeatures)]


def feature_factory(name, value, fid, version):
    return {
        "name": name,
        "value": value,
        "fid": fid,
        "version": version
    }


def generate_data(ndocs, offset=0):
    return [object_factory(i + offset) for i in range(ndocs)]


def load_data(connection: MongoConnection, ndocs: int, offset: int = 0):
    data = generate_data(ndocs, offset)
    connection.database["object"].insert_many(data, ordered=False)
