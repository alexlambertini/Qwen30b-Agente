import unittest
from report import summarize
class T(unittest.TestCase):
    def test_sum(self): self.assertEqual(summarize(["a, 1.5","b, 2"]), 3.5)
    def test_thousands(self): self.assertEqual(summarize(["a, 1,200.50","b, 2"]), 1202.5)
    def test_blank(self): self.assertEqual(summarize(["a, 1","", "  "]), 1)
