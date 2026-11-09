import unittest
from cart import total
class T(unittest.TestCase):
    def test_plain(self): self.assertEqual(total([{"price":10,"qty":2}]), 20)
    def test_discount(self): self.assertEqual(total([{"price":10,"qty":2}], 10), 18)
