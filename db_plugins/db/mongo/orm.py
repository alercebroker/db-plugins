"""Main classes for using the Mongo ORM"""
from pymongo import MongoClient


class Metadata:
    database = "DEFAULT_DATABASE"
    collections = {}

    def create_all(self, client: MongoClient, database: str = None):
        self.database = database or self.database
        db = client[self.database]
        for c in self.collections:
            collection = db[c]
            collection.create_indexes(self.collections[c]["indexes"])

    def drop_all(self, client: MongoClient, database: str = None):
        self.database = database or self.database
        client.drop_database(self.database)


class ModelMetadata:
    def __init__(self, tablename: str, fields: dict, indexes: list):
        self.tablename = tablename
        self.fields = fields
        self.indexes = indexes

    def __repr__(self):
        dict_repr = {
            "tablename": self.tablename,
            "fields": self.fields,
            "indexes": self.indexes,
        }
        return str(dict_repr)


class BaseMetaClass(type):
    """Metaclass for Base model class that creates mappings."""

    metadata = Metadata()

    def __new__(mcs, name, bases, attrs):
        """Create class with mappings and other metadata."""
        cls = super().__new__(mcs, name, bases, attrs)

        tablename = attrs.get("__tablename__", "")
        indexes = attrs.get("__table_args__", [])
        fields = {k: v for k, v in attrs.items() if isinstance(v, Field)}
        try:
            fields["extra_fields"] = SpecialField(cls.create_extra_fields)
        except AttributeError:
            pass
        if tablename:
            mcs.metadata.collections[tablename] = {"indexes": indexes, "fields": fields}
        cls._meta = ModelMetadata(tablename, fields, indexes)
        return cls


class Field:
    pass


class SpecialField(Field):
    def __init__(self, callback):
        self.callback = callback
