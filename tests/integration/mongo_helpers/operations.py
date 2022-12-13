from db_plugins.db.mongo.connection import MongoConnection


def _get_execution_stats(query_info, out=False):
    execution_stats = query_info["executionStats"]
    total_ms = execution_stats["executionTimeMillis"]
    docs_examined = execution_stats["totalDocsExamined"]
    docs_returned = execution_stats["nReturned"]
    keys_examined = execution_stats["totalKeysExamined"]

    if out:
        print(f'\nResult\n  Time: {total_ms} ms\n  Docs returned {docs_returned}\n  Docs examined: {docs_examined}\n  Keys examined: {keys_examined}')

    return total_ms, docs_examined, keys_examined


def _get_dbstats(dbstats_info):
    index_size = dbstats_info["indexSize"]
    total_size = dbstats_info["totalSize"]

    conv = 1024 ** 2
    print(f'\nDB\n  Total size: {total_size / conv:.1f} MB\n  Index size {index_size / conv: .1f} MB\n  Index proportion: {index_size / total_size:.3f}')


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

    dbstats = connection.database.command("dbstats")
    _get_dbstats(dbstats)

    return _get_execution_stats(query_info, True)
