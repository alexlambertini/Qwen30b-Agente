import unittest
from pager import paginate
class T(unittest.TestCase):
    def test_exact(self): self.assertEqual(paginate([1,2,3,4],2), [[1,2],[3,4]])
    def test_rest(self): self.assertEqual(paginate([1,2,3,4,5],2), [[1,2],[3,4],[5]])
    def test_empty(self): self.assertEqual(paginate([],3), [])
if __name__=="__main__": unittest.main()
