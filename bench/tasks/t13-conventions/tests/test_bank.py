import sys
import unittest

sys.path.insert(0, "src")

from bank import Account  # noqa: E402
from errors import InsufficientFunds  # noqa: E402


class AccountTest(unittest.TestCase):
    def test_deposit(self):
        self.assertEqual(Account("ana").deposit(100), 100)

    def test_withdraw_insufficient(self):
        with self.assertRaises(InsufficientFunds):
            Account("ana", 50).withdraw(51)


if __name__ == "__main__":
    unittest.main()
