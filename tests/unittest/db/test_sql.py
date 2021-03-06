from db_plugins.db.sql import models, Pagination, SQLConnection, SQLQuery, Pagination
import unittest
from unittest import mock
from alchemy_mock.mocking import UnifiedAlchemyMagicMock
import json
import time
import datetime


class SQLConnectionTest(unittest.TestCase):
    def setUp(self):
        self.config = {}
        self.session_options = {
            "autocommit": False,
            "autoflush": True,
        }
        mock_engine = mock.Mock()
        self.db = SQLConnection(engine=mock_engine, Session=UnifiedAlchemyMagicMock)

    def tearDown(self):
        del self.db

    @mock.patch("db_plugins.db.sql.SQLConnection.create_session")
    def test_connect_not_scoped(self, mock_create_session):
        self.db.connect(
            config=self.config, session_options=self.session_options, use_scoped=False
        )
        self.assertIsNotNone(self.db.engine)
        self.assertIsNotNone(self.db.Base)
        self.assertIs(self.db.Session, UnifiedAlchemyMagicMock)
        mock_create_session.assert_called_once()

    @mock.patch("db_plugins.db.sql.SQLConnection.create_scoped_session")
    def test_connect_scoped(self, mock_create_session):
        self.db.connect(
            config=self.config, session_options=self.session_options, use_scoped=True
        )
        self.assertIsNotNone(self.db.engine)
        self.assertIsNotNone(self.db.Base)
        self.assertIs(self.db.Session, UnifiedAlchemyMagicMock)
        mock_create_session.assert_called_once()

    def test_create_session(self):
        self.db.create_session()
        self.assertIsInstance(self.db.session, UnifiedAlchemyMagicMock)

    def test_create_scoped_session(self):
        self.db.Base = mock.Mock()
        self.db.create_scoped_session()
        self.assertIsNotNone(self.db.session)
        self.assertIsNotNone(self.db.Base.query)

    def test_create_db(self):
        self.db.Base = mock.Mock()
        self.db.create_db()
        self.db.Base.metadata.create_all.assert_called_once_with(bind=self.db.engine)

    def test_drop_db(self):
        self.db.Base = mock.Mock()
        self.db.drop_db()
        self.db.Base.metadata.drop_all.assert_called_once_with(bind=self.db.engine)

    def test_query(self):
        model = models.Object
        self.db.session = UnifiedAlchemyMagicMock()
        query = self.db.query(model)
        self.db.session.query.assert_called_once_with(model)


class SQLQueryTest(unittest.TestCase):
    # @classmethod
    # def setUpClass(self):
    #     config = {"SQLALCHEMY_DATABASE_URL": "sqlite:///:memory:"}
    #     session_options = {
    #         "autocommit": False,
    #         "autoflush": True,
    #     }
    #     self.db = SQLConnection()
    #     self.db.connect(config=config, session_options=session_options)

    # @classmethod
    # def tearDownClass(self):
    #     self.db.drop_db()
    #     self.db.session.close()

    def setUp(self):
        self.session = UnifiedAlchemyMagicMock()
        self.query = SQLQuery([], self.session)

    def tearDown(self):
        del self.session
        del self.query

    def test_check_exist(self):
        self.session.scalar.return_value = True
        res = self.query.check_exists(model=models.Object, filter_by={})
        self.session.scalar.assert_called_once()
        self.assertTrue(res)

    def test_get_or_create_not_created(self):
        obj = models.Object()
        self.session.add(obj)
        instance, created = self.query.get_or_create(
            model=models.Object, filter_by={}, **{}
        )
        self.session.first.assert_called_once()
        self.session.commit.assert_not_called()
        self.assertFalse(created)

    def test_get_or_create_created(self):
        instance, created = self.query.get_or_create(
            model=models.Object, filter_by={}, **{}
        )
        self.assertTrue(created)
        self.session.commit.assert_called_once()

    def test_update(self):
        obj = models.Object()
        self.session.add(obj)
        self.query.update(obj, {"oid": "test"})
        self.assertEqual(obj.oid, "test")

    @mock.patch("db_plugins.db.sql.insert")
    def test_bulk_insert_no_objects(self, mock_insert):
        self.query.bulk_insert([])
        mock_insert.assert_not_called()

    def test_bulk_insert(self):
        pass

    def test_paginate(self):
        self.query = SQLQuery(models.Object, self.session)
        page = self.query.paginate()
        self.assertIsInstance(page, Pagination)

    def test_find_one_doesnt_exist(self):
        one = self.query.find_one(models.Object)
        self.assertFalse(one)

    def test_find_one_exists(self):
        obj = models.Object()
        self.session.add(obj)
        one = self.query.find_one(models.Object)
        self.assertIsInstance(one, models.Object)

    def test_find_paginate(self):
        self.query = SQLQuery(models.Object, self.session)
        page = self.query.find(model=models.Object)
        self.assertIsInstance(page, Pagination)

    def test_find_no_paginate(self):
        self.query = SQLQuery(models.Object, self.session)
        found = self.query.find(model=models.Object, paginate=False)
        self.assertIsInstance(found, list)
