import unittest
from store import Store
class T(unittest.TestCase):
    def test_count(self):
        s = Store(); s.add("a", 1, "x"); self.assertEqual(s.count(), 1)
if __name__ == "__main__": unittest.main()
