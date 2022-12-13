from db_plugins.db.mongo.connection import MongoConnection


def _get_execution_stats(query_info, fh=None):
    execution_stats = query_info["executionStats"]
    total_ms = execution_stats["executionTimeMillis"]
    docs_examined = execution_stats["totalDocsExamined"]
    docs_returned = execution_stats["nReturned"]
    keys_examined = execution_stats["totalKeysExamined"]

    if fh:
        fh.write(f',{total_ms},{docs_returned},{docs_examined},{keys_examined}\n')
        print(f"{total_ms},{docs_returned},{docs_examined},{keys_examined}")

    return total_ms, docs_examined, keys_examined


def _get_dbstats(dbstats_info, fh=None):
    index_size = dbstats_info["indexSize"]
    total_size = dbstats_info["totalSize"]

    conv = 1024 ** 2
    if fh:
        fh.write(f',{total_size / conv:.3f},{index_size / conv:.3f}')


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


def find_objects_by_probability(connection: MongoConnection, classifier_name, class_name, fh=None):
    query_info = connection.database["object"].find(
        {"probabilities":
            {"$elemMatch": {
                "probability": {"$gte": 0.7},
                "classifier_name": classifier_name,
                "class_name": class_name,
                "ranking": 1
            }
            }}).explain()

    dbstats = connection.database.command("dbstats")
    _get_dbstats(dbstats, fh)
    return _get_execution_stats(query_info, fh)
