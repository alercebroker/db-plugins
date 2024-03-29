from db_plugins.db.sql.models import Object
from db_plugins.db.sql.connection import (
    SQLConnection,
    create_engine,
    sessionmaker,
    Base,
)

from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.orm import Query
from sqlalchemy.inspection import inspect
import pytest
import unittest


@pytest.mark.usefixtures("psql_service")
class SQLConnectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        config = {
            "ENGINE": "postgresql",
            "HOST": "localhost",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "PORT": 5432,
            "DB_NAME": "postgres",
        }
        self.config = {
            "SQLALCHEMY_DATABASE_URL": f"{config['ENGINE']}://{config['USER']}:{config['PASSWORD']}@{config['HOST']}:{config['PORT']}/{config['DB_NAME']}"
        }
        self.session_options = {
            "autocommit": False,
            "autoflush": True,
        }
        self.db = SQLConnection()

    def tearDown(self):
        if self.db.Base and self.db.engine:
            self.db.Base.metadata.drop_all(bind=self.db.engine)

    def test_connect_not_scoped(self):
        self.db.connect(
            self.config, session_options=self.session_options, use_scoped=False
        )
        self.assertIsNotNone(self.db.engine)
        self.assertIsNotNone(self.db.session)

    def test_connect_scoped(self):
        session_options = self.session_options
        session_options["autoflush"] = False
        self.db.connect(self.config, session_options=session_options, use_scoped=True)
        self.assertIsNotNone(self.db.engine)
        self.assertIsNotNone(self.db.session)

    def test_create_session(self):
        engine = create_engine(self.config["SQLALCHEMY_DATABASE_URL"])
        Session = sessionmaker(bind=engine, **self.session_options)
        self.db.Session = Session
        self.db.create_session(use_scoped=False)
        self.assertIsNotNone(self.db.session)

    def test_create_scoped_session(self):
        engine = create_engine(self.config["SQLALCHEMY_DATABASE_URL"])
        session_options = self.session_options
        session_options["autoflush"] = False
        Session = sessionmaker(bind=engine, **session_options)
        self.db.Session = Session
        self.db.Base = Base
        self.db.create_session(use_scoped=True)
        self.assertIsNotNone(self.db.session)

    def test_create_db(self):
        engine = create_engine(self.config["SQLALCHEMY_DATABASE_URL"])
        self.db.engine = engine
        self.db.Base = Base
        self.db.create_db()
        inspector = inspect(engine)
        self.assertGreater(len(inspector.get_table_names()), 0)

    def test_drop_db(self):
        engine = create_engine(self.config["SQLALCHEMY_DATABASE_URL"])
        self.db.engine = engine
        self.db.Base = Base
        self.db.Base.metadata.create_all(bind=self.db.engine)
        self.db.drop_db()
        inspector = inspect(engine)
        self.assertEqual(len(inspector.get_table_names()), 0)

    def test_query(self):
        query = self.db.query(Object)
        self.assertIsInstance(query, Query)