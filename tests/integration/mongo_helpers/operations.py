from pprint import pprint
from db_plugins.db.mongo.connection import MongoConnection


def _get_execution_stats(query_info, command=False):
    execution_stats = query_info["executionStats"]
    total_ms = execution_stats["executionTimeMillis"]
    docs_examined = execution_stats["totalDocsExamined"]
    keys_examined = execution_stats["totalKeysExamined"]

    if command:
        pprint(execution_stats)

    return total_ms, docs_examined, keys_examined


def find_objects_batch_explained(connection: MongoConnection, aid_list: list):
    query_info = connection.database["object"].find(
        {"_id": {"$in": aid_list}}, {"probabilities": True}
    ).explain()

    return _get_execution_stats(query_info)


def find_object_explained(connection: MongoConnection, aid: str):
    query_info = connection.database["object"].find(
        {"_id": aid}
    ).explain()

    return _get_execution_stats(query_info)


def find_objects_by_probability(connection: MongoConnection, classifier_name, class_name):
    query_info = connection.database["object"].find(
        {"probabilities":
            {"$elemMatch": {
                "probability": {"$gte": 0.9},
                "classifier_name": classifier_name,
                "class_name": class_name,
                "ranking": 1
            }
            }}).explain()

    pprint(connection.database.stats())

    return _get_execution_stats(query_info, True)
