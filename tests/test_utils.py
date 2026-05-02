import unittest
from src.models import Aeroplane

class TestUtils(unittest.TestCase):

    def setUp(self):
        """Создаем тестовый набор самолетов перед каждым тестом."""
        self.p1 = Aeroplane("A1", "USA", 100.0, 5000.0)
        self.p2 = Aeroplane("A2", "UK", 200.0, 10000.0)
        self.p3 = Aeroplane("A3", "USA", 150.0, 8000.0)
        self.planes = [self.p1, self.p2, self.p3]

    def test_filter_aeroplanes(self):
        """Тест фильтрации по стране регистрации."""
        filtered = filter_aeroplanes(self.planes, ["USA"])
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(p.origin_country == "USA" for p in filtered))

    def test_get_aeroplanes_by_altitude(self):
        """Тест фильтрации по диапазону высот."""
        ranged = get_aeroplanes_by_altitude(self.planes, "6000 - 11000")
        self.assertEqual(len(ranged), 2)
        self.assertTrue(all(6000 <= p.altitude <= 11000 for p in ranged))

