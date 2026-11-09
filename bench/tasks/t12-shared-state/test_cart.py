import unittest

from cart import Cart


class CartTest(unittest.TestCase):
    def test_total(self):
        c = Cart("ana")
        c.add("livro", 50)
        c.apply_coupon("DEZ", 10)
        self.assertEqual(c.total(), 45)


if __name__ == "__main__":
    unittest.main()
