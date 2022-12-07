import unittest
import pytest

@pytest.mark.usefixtures("mongo_service")
class MongoConnectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testVoid(self):
        self.assertFalse(False)