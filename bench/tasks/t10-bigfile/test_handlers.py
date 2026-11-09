import unittest

from handlers import ValidationError, dispatch


class HandlersTest(unittest.TestCase):
    def test_payment(self):
        self.assertEqual(dispatch("payment", {"account": "a", "amount": 5})["sign"], 1)

    def test_payment_rejects_zero(self):
        with self.assertRaises(ValidationError):
            dispatch("payment", {"account": "a", "amount": 0})


if __name__ == "__main__":
    unittest.main()
