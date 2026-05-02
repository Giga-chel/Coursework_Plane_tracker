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

