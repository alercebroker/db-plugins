from test_core import *
from db_plugins.db.sql.models import *
from db_plugins.db.sql import Pagination, SQLConnection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import unittest
import json
import time
import datetime


class DatabaseConnectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        config = {"SQLALCHEMY_DATABASE_URL": "sqlite:///:memory:"}
        session_options = {
            "autocommit": False,
            "autoflush": True,
        }
        self.db = SQLConnection()
        self.db.connect(config=config, session_options=session_options)

    @classmethod
    def tearDownClass(self):
        self.db.drop_db()
        self.db.session.close()

    def setUp(self):
        self.db.create_db()
        obj = Object(
            oid="ZTF1",
            ndet=1,
            lastmjd=1.0,
            meanra=1.0,
            meandec=1.0,
            sigmadec=1.0,
            deltajd=1.0,
            firstmjd=1.0,
        )
        self.db.session.add(obj)
        class_object = Class(fullname="Super Nova", name="SN")
        self.db.session.add(class_object)
        classifier = Classifier(name="test", version="1.0.0-test")
        self.db.session.add(classifier)
        taxonomy = Taxonomy(
            class_name=class_object.name,
            classifier_name=classifier.name,
            classifier_version=classifier.version,
        )
        self.db.session.add(taxonomy)
        classification = Probability(
            oid=obj.oid,
            classifier_name=taxonomy.classifier_name,
            classifier_version=taxonomy.classifier_version,
            class_name=taxonomy.class_name,
            probability=1.0,
            ranking=1,
        )
        self.db.session.add(classification)
        self.db.session.commit()

    def tearDown(self):
        self.db.session.close()
        self.db.drop_db()

    def test_get_or_create(self):
        instance, created = self.db.session.query().get_or_create(
            Object, {"oid": "ZTF1"}
        )
        self.assertIsInstance(instance, Object)
        self.assertFalse(created)

    def test_check_exists(self):
        self.assertTrue(self.db.session.query().check_exists(Object, {"oid": "ZTF1"}))

    def test_update(self):
        instance = (
            self.db.session.query(Object).filter(Object.oid == "ZTF1").one_or_none()
        )
        updated = self.db.session.query().update(instance, {"oid": "ZTF2"})
        self.assertEqual(updated.oid, "ZTF2")

    def test_bulk_insert(self):
        objs = [{"oid": "ZTF2"}, {"oid": "ZTF3"}]
        self.db.session.query().bulk_insert(objs, Object)
        objects = self.db.session.query(Object).all()
        self.assertEqual(len(objects), 3)

    def test_paginate(self):
        pagination = self.db.session.query(Object).paginate()
        self.assertIsInstance(pagination, Pagination)
        self.assertEqual(pagination.total, 1)
        self.assertEqual(pagination.items[0].oid, "ZTF1")

    def test_find_one(self):
        obj = self.db.query(Object).find_one(filter_by={"oid": "ZTF1"})
        self.assertIsInstance(obj, Object)

    def test_find(self):
        obj_page = self.db.query(Object).find()
        self.assertIsInstance(obj_page, Pagination)
        self.assertEqual(obj_page.total, 1)
        self.assertEqual(obj_page.items[0].oid, "ZTF1")

    def test_find_paginate_false(self):
        obj_page = self.db.query(Object).find(paginate=False)
        self.assertIsInstance(obj_page, list)

class ScopedDatabaseConnectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        config = {"SQLALCHEMY_DATABASE_URL": "sqlite:///:memory:"}
        session_options = {
            "autocommit": False,
            "autoflush": False,
        }
        self.db = SQLConnection()
        self.db.connect(config=config, session_options=session_options, use_scoped=True)

    @classmethod
    def tearDownClass(self):
        self.db.drop_db()
        self.db.session.remove()

    def setUp(self):
        self.db.create_db()
        obj = Object(
            oid="ZTF1",
            ndet=1,
            lastmjd=1.0,
            meanra=1.0,
            meandec=1.0,
            sigmadec=1.0,
            deltajd=1.0,
            firstmjd=1.0,
        )
        self.db.session.add(obj)
        self.db.session.commit()

    def tearDown(self):
        self.db.drop_db()
        self.db.session.remove()

    def test_query_property(self):
        self.assertEqual(len(Object.query.all()), 1)
        self.assertEqual(Object.query.first().oid, "ZTF1")

    def test_method_access_from_session(self):
        instance, created = self.db.session.query().get_or_create(
            model=Object, filter_by={"oid": "ZTF1"}
        )
        self.assertIsInstance(instance, Object)
        self.assertFalse(created)

    def test_method_access_from_query_property(self):
        instance, created = Object.query.get_or_create(filter_by={"oid": "ZTF1"})
        self.assertIsInstance(instance, Object)
        self.assertFalse(created)


class ClassTest(unittest.TestCase, GenericClassTest):
    pass


class TaxonomyTest(GenericTaxonomyTest, unittest.TestCase):
    pass


class ClassifierTest(GenericClassifierTest, unittest.TestCase):
    pass


class XMatchTest(GenericXMatchTest, unittest.TestCase):
    pass


class MagnitudeStatisticsTest(GenericMagnitudeStatisticsTest, unittest.TestCase):
    pass


class ClassificationTest(GenericClassificationTest, unittest.TestCase):
    pass


class ObjectTest(GenericObjectTest, unittest.TestCase):
    @classmethod
    def setUpClass(self):
        config = {"SQLALCHEMY_DATABASE_URL": "sqlite:///:memory:"}
        session_options = {
            "autocommit": False,
            "autoflush": False,
        }
        self.db = SQLConnection()
        self.db.connect(config=config, session_options=session_options)

    @classmethod
    def tearDownClass(self):
        self.db.drop_db()
        self.db.session.close()

    def setUp(self):
        self.db.create_db()
        class_ = Class(fullname="Super Nova", name="SN")
        classifier = Classifier(name="C1", version="1.0.0-test")
        self.model = Object(
            oid="ZTF1",
            ndet=1,
            lastmjd=1.0,
            meanra=1.0,
            meandec=1.0,
            sigmara=1.0,
            sigmadec=1.0,
            deltajd=1.0,
            firstmjd=1.0,
        )
        self.model.magstats.append(
            MagStats(
                fid=1,
                stellar=True,
                corrected=True,
                ndet=1,
                ndubious=1,
                dmdt_first=0.13,
                dm_first=0.12,
                sigmadm_first=1.4,
                dt_first=2.0,
                magmean=19.0,
                magmedian=20,
                magmax=1.4,
                magmin=1.4,
                magsigma=1.4,
                maglast=1.4,
                magfirst=1.4,
                firstmjd=1.4,
                lastmjd=1.4,
                step_id_corr="testing_id",
            )
        )
        self.model.probabilities.append(
            Probability(
                class_name=class_.name,
                probability=1.0,
                classifier_name=classifier.name,
                classifier_version=classifier.version,
                ranking=1,
            )
        )
        feature_version = FeatureVersion(version="1.0.0-test")
        feature = Feature(
            oid=self.model.oid,
            name="testfeature",
            value=0.5,
            fid=1,
            version=feature_version.version,
        )
        self.model.detections.append(
            Detection(
                candid="t",
                mjd=1,
                fid=1,
                ra=1,
                dec=1,
                rb=1,
                magap=1,
                magpsf=1,
                sigmapsf=1,
                sigmagap=1,
            )
        )
        self.model.non_detections.append(NonDetection(mjd=1, fid=1, diffmaglim=1))
        self.db.session.add(self.model)
        self.db.session.commit()

    def tearDown(self):
        self.db.session.close()
        self.db.drop_db()


class FeaturesTest(GenericFeaturesTest, unittest.TestCase):
    pass


class NonDetectionTest(GenericNonDetectionTest, unittest.TestCase):
    pass


class DetectionTest(GenericDetectionTest, unittest.TestCase):
    pass
