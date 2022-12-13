from db_plugins.db.mongo.connection import MongoConnection
from mongo_helpers.operations import (
    find_object_explained, find_objects_batch_explained, find_objects_by_probability
)
from mongo_helpers.data_loader import load_data
import unittest
import pytest


@pytest.mark.usefixtures("mongo_service")
class MongoConnectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        config = {
            "HOST": "localhost",
            "PORT": 27017,
            "DATABASE": "test_database",
            "USERNAME": "root",
            "PASSWORD": "example"
        }

        db = MongoConnection()
        db.connect(config=config)
        db.create_db()
        load_data(db)
        self.db = db

    @classmethod
    def tearDownClass(self):
        self.db.drop_db()

    def test_find_single_object(self):
        total_ms, docs_examined, _ = find_object_explained(self.db, "aid21")
        self.assertEqual(docs_examined, 1)
        self.assertEqual(total_ms, 0)

    def test_find_object_batch(self):
        total_ms, docs_examined, _ = find_objects_batch_explained(
            self.db, ["aid5", "aid20", "aid48", "aid3405", "aid10", "aid5566"])
        self.assertLessEqual(docs_examined, 20)
        self.assertLessEqual(total_ms, 5000)

    def test_find_objects_by_probs(self):
        total_ms, docs_examined, _ = find_objects_by_probability(self.db, "stamp_classifier", "CLASS1")
        self.assertLessEqual(docs_examined, 500)
        self.assertLessEqual(total_ms, 5000)
