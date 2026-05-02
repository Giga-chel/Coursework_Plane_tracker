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

