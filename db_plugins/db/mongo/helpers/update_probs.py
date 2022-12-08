from db_plugins.db.mongo.connection import MongoConnection
from pymongo import UpdateOne

"""
Helper function to create or update the probabilities for an object
"""


def get_probabilities(connection: MongoConnection, aids: list):
    probabilities = connection.database["object"].find(
        {"_id": {"$in": aids}}, {"probabilities": True}
    )
    return {item["_id"]: item["probabilities"] for item in probabilities}


def get_db_operations(
    classifier: str,
    version: str,
    aid: str,
    object_probabilities: list,
    probabilities: dict,
):
    """
    Check if this is really efficient
    """
    # sort by probabilities (for rank)
    sorted_classes_and_prob_list = sorted(
        probabilities.items(), key=lambda val: val[1], reverse=True
    )

    # Remove all existing probabilities for given classifier and version (if any)
    object_probabilities = [
        item
        for item in object_probabilities
        if item["classifier_name"] != classifier
        or item["classifier_version"] != version
    ]
    # Add all new probabilities
    object_probabilities.extend(
        [
            {
                "classifier_version": version,
                "classifier_name": classifier,
                "class_name": object_class,
                "probability": prob,
                "ranking": idx + 1,
            }
            for idx, (object_class, prob) in enumerate(sorted_classes_and_prob_list)
        ]
    )

    operation = UpdateOne(
        {"_id": aid}, {"$set": {"probabilities": object_probabilities}}
    )

    return operation


def create_or_update_probabilities(
    connection: MongoConnection,
    classifier: str,
    version: str,
    aid: str,
    probabilities: dict,
):
    object_probs = get_probabilities(connection, [aid])

    connection.database["object"].bulk_write(
        [get_db_operations(classifier, version, aid, object_probs[aid], probabilities)],
        ordered=False,
    )


def create_or_update_probabilities_bulk(
    connection: MongoConnection,
    classifier: str,
    version: str,
    aids: list,
    probabilities: list,
):
    """
    Bulk update using the actual bulk object of pymongo
    """
    db_operations = []

    # no warrants that probs will have the same aid order
    object_probabilities = get_probabilities(connection, aids)

    for aid, probs in zip(aids, probabilities):
        db_operations.append(
            get_db_operations(
                classifier, version, aid, object_probabilities[aid], probs
            )
        )

    connection.database["object"].bulk_write(db_operations, ordered=False)
