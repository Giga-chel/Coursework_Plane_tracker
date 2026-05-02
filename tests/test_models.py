import unittest
from src.models import Aeroplane


class TestAeroplane(unittest.TestCase):

    def test_initialization_and_encapsulation(self):
        """Тест правильной инициализации и работы свойств (property)."""
        plane = Aeroplane("UAL1621", "United States", 268.79, 10203.18, False)
        self.assertEqual(plane.callsign, "UAL1621")
        self.assertEqual(plane.origin_country, "United States")
        self.assertEqual(plane.velocity, 268.79)
        self.assertEqual(plane.altitude, 10203.18)
        self.assertFalse(plane.on_ground)

    def test_validation_none_values(self):
        """Тест валидации данных (замена None на значения по умолчанию)."""
        plane = Aeroplane(None, None, None, None, None)
        self.assertEqual(plane.callsign, "N/A")
        self.assertEqual(plane.origin_country, "Unknown")
        self.assertEqual(plane.velocity, 0.0)
        self.assertEqual(plane.altitude, 0.0)

    def test_comparison_methods(self):
        """Тест методов сравнения по высоте и скорости."""
        p1 = Aeroplane("A", "Country1", 100.0, 5000.0)
        p2 = Aeroplane("B", "Country2", 200.0, 10000.0)

        self.assertTrue(p1 < p2)  # Тест __lt__ (по высоте)
        self.assertTrue(p2.is_higher_than(p1))
        self.assertTrue(p2.is_faster_than(p1))
        self.assertFalse(p1.is_faster_than(p2))

    def test_cast_to_object_list(self):
        """Тест конвертации сырых данных API в список объектов."""
        raw_data = [
            [0, "TST123", "France", 0, 0, 0, 0, 0, False, 150.5, 0, 0, 0, 8000.0],
            [1, None, None, 0, 0, 0, 0, 0, True, None, 0, 0, 0, None]  # Самолет на земле
        ]
        planes = Aeroplane.cast_to_object_list(raw_data)

        self.assertEqual(len(planes), 2)
        self.assertEqual(planes[0].callsign, "TST123")
        self.assertEqual(planes[0].velocity, 150.5)
        self.assertEqual(planes[1].callsign, "N/A")  # Проверка работы с None
        self.assertTrue(planes[1].on_ground)

if __name__ == '__main__':
    unittest.main()
