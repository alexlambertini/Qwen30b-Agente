import unittest

from repo import InMemoryRepo
from service import InventoryService


class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.svc = InventoryService(InMemoryRepo())

    def test_add_and_total(self):
        self.svc.add_item("parafuso", 10, 0.5)
        self.svc.add_item("porca", 4, 0.25)
        self.assertEqual(self.svc.total_value(), 6.0)

    def test_remove_stock(self):
        self.svc.add_item("parafuso", 10, 0.5)
        self.assertEqual(self.svc.remove_stock("parafuso", 3).quantity, 7)


if __name__ == "__main__":
    unittest.main()
