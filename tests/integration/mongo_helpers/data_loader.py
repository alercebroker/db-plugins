from db_plugins.db.mongo.connection import MongoConnection
from db_plugins.db.mongo.models import Object
import random

random.seed(42)
n_docs = int(1e5)
n_class = 10


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
        probabilities=generate_probabilities()
    )


def generate_probabilities():
    classifiers = [
        "stamp_classifier",
        "lc_classifier"
    ]
    classes = [f"CLASS{i + 1}" for i in range(n_class)]

    generated_probabilities = []

    for classifier in classifiers:
        random.shuffle(classes)
        class_probs = []
        for i in range(n_class):
            off = 0 if i == 0 else sum(class_probs)
            if i == n_class - 1:
                class_probs.append(1 - off)
            else:
                class_probs.append(random.random() * (1 - off))
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


def generate_data(ndocs, offset=0):
    return [object_factory(i + offset) for i in range(ndocs)]


def load_data(connection: MongoConnection, ndocs: int, offset: int = 0):
    data = generate_data(ndocs, offset)
    connection.database["object"].insert_many(data, ordered=False)