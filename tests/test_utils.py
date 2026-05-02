import unittest
from src.utils import filter_aeroplanes, get_aeroplanes_by_altitude, get_top_aeroplanes
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

    def test_get_top_aeroplanes_by_altitude(self):
        """Тест получения Топ N по высоте."""
        top_2 = get_top_aeroplanes(self.planes, 2)
        self.assertEqual(len(top_2), 2)
        self.assertEqual(top_2[0].callsign, "A2") # 10000 м
        self.assertEqual(top_2[1].callsign, "A3") # 8000 м

    def test_get_top_aeroplanes_by_velocity(self):
        """Тест получения Топ N по скорости."""
        top_1 = get_top_aeroplanes(self.planes, 1, sort_by='velocity')
        self.assertEqual(top_1[0].callsign, "A2") # 200 м/с

if __name__ == '__main__':
    unittest.main()
