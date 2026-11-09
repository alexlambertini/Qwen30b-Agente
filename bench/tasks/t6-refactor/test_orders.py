import unittest
from orders import price_retail, price_wholesale
class T(unittest.TestCase):
    def test_r(self):
        self.assertEqual(price_retail(10, 5), 50)
        self.assertEqual(price_retail(10, 10), 95)
        self.assertEqual(price_retail(10, 100), 850)
    def test_w(self):
        self.assertEqual(price_wholesale(10, 100), 900)
        self.assertEqual(price_wholesale(10, 200), 1440)
