import unittest
from db_plugins.db.mongo import models


class MongoModelsTest(unittest.TestCase):
    def test_object_creates(self):
        o = models.Object(
            aid="aid",
            oid="oid",
            tid="tid",
            lastmjd="lastmjd",
            firstmjd="firstmjd",
            corrected=True,
            stellar=True,
            sigmara=.1,
            sigmadec=.2,
            meanra=100.0,
            meandec=50.0,
            ndet="ndet",
        )
        self.assertIsInstance(o, models.Object)
        self.assertIsInstance(o, dict)
        self.assertEqual(o["loc"], {"type": "Point", "coordinates": [-80.0, 50]})
        self.assertEqual(
            o._meta.tablename,
            models.Object.__tablename__,
        )

    def test_object_fails_creation(self):
        with self.assertRaises(AttributeError) as e:
            models.Object()
        self.assertEqual(str(e.exception), "Object model needs _id attribute")

    def test_detection_creates(self):
        d = models.Detection(
            tid="tid",
            aid="aid",
            oid="oid",
            candid="candid",
            mjd="mjd",
            fid="fid",
            ra="ra",
            dec="dec",
            rb="rb",
            mag="mag",
            e_mag="e_mag",
            mag_corr="mag_corr",
            stellar="stellar",
            e_mag_corr="e_mag_corr",
            e_mag_corr_ext="e_mag_corr_ext",
            parent_candidate="parent_candidate",
            e_ra="e_ra",
            e_dec="e_dec",
            isdiffpos="isdiffpos",
            corrected="corrected",
            dubious="dubious",
            parent_candid="parent_candid",
            has_stamp="has_stamp",
            step_id_corr="step_id_corr",
            rbversion="rbversion",
        )
        self.assertIsInstance(d, models.Detection)
        self.assertIsInstance(d, dict)
        self.assertEqual(d["aid"], "aid")

    def test_detection_fails_creation(self):
        with self.assertRaisesRegex(AttributeError, "Detection model needs .+? attribute"):
            models.Detection()

    def test_detection_with_extra_fields(self):
        o = models.Detection(
            tid="tid",
            aid="aid",
            oid="oid",
            candid="candid",
            mjd="mjd",
            fid="fid",
            ra="ra",
            dec="dec",
            mag="mag",
            e_mag="e_mag",
            mag_corr="mag_corr",
            e_mag_corr="e_mag_corr",
            e_mag_corr_ext="e_mag_corr_ext",
            dubious="dubious",
            e_ra="e_ra",
            e_dec="e_dec",
            isdiffpos="isdiffpos",
            corrected="corrected",
            stellar="stellar",
            has_stamp="has_stamp",
            extra="extra",
        )
        self.assertEqual(o["extra_fields"], {"extra": "extra"})
        o = models.Detection(
            tid="tid",
            aid="aid",
            oid="oid",
            candid="candid",
            mjd="mjd",
            fid="fid",
            ra="ra",
            dec="dec",
            rb="rb",
            mag="mag",
            e_mag="e_mag",
            mag_corr="mag_corr",
            e_mag_corr="e_mag_corr",
            e_mag_corr_ext="e_mag_corr_ext",
            parent_candidate="parent_candidate",
            dubious="dubious",
            e_ra="e_ra",
            e_dec="e_dec",
            stellar="stellar",
            isdiffpos="isdiffpos",
            corrected="corrected",
            has_stamp="has_stamp",
            extra_fields={"extra": "extra"},
        )
        self.assertEqual(o["extra_fields"], {"extra": "extra"})

    def test_non_detection_creates(self):
        o = models.NonDetection(
            aid="aid",
            oid="oid",
            tid="sid",
            mjd="mjd",
            diffmaglim="diffmaglim",
            fid="fid",
        )
        self.assertIsInstance(o, models.NonDetection)
        self.assertIsInstance(o, dict)
        self.assertEqual(o["aid"], "aid")

    def test_non_detection_fails_creation(self):
        with self.assertRaisesRegex(AttributeError, "NonDetection model needs .+ attribute"):
            models.NonDetection()
        # self.assertEqual(str(e.exception), "NonDetection model needs aid attribute")

    def test_non_detection_with_extra_fields(self):
        o = models.NonDetection(
            aid="aid",
            oid="oid",
            tid="tid",
            mjd="mjd",
            diffmaglim="diffmaglim",
            fid="fid",
            extra="extra",
        )
        self.assertEqual(o["extra_fields"], {"extra": "extra"})
        o = models.NonDetection(
            aid="aid",
            oid="oid",
            tid="tid",
            mjd="mjd",
            diffmaglim="diffmaglim",
            fid="fid",
            extra_fields={"extra": "extra"},
        )
        self.assertEqual(o["extra_fields"], {"extra": "extra"})

    def test_taxonomy_creates(self):
        o = models.Taxonomy(
            classifier_name="classifier",
            classifier_version="test-1.0.0",
            classes=["class1", "class2"],
        )
        self.assertIsInstance(o, models.Taxonomy)
        self.assertIsInstance(o, dict)
        self.assertEqual(o["classifier_name"], "classifier")

    def test_taxonomy_fails_creation(self):
        with self.assertRaises(AttributeError) as e:
            models.Taxonomy()
        self.assertEqual(
            str(e.exception), "Taxonomy model needs classifier_name attribute"
        )

    def test_taxonomy_with_extra_fields_ignores_them(self):
        as_dict = dict(
            classifier_name="classifier",
            classifier_version="test-1.0.0",
            classes=["class1", "class2"],
        )
        o = models.Taxonomy(extra="extra", **as_dict)
        self.assertDictEqual(o, as_dict)
