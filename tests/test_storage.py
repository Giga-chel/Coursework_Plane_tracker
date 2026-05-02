import unittest
import os
import tempfile
from src.storage import JSONSaver
from src.models import Aeroplane


class TestJSONSaver(unittest.TestCase):

    def setUp(self):
        """Создаем временный файл для каждого теста."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
        self.saver = JSONSaver(self.temp_file)
        self.plane1 = Aeroplane("TST1", "Germany", 120.0, 6000.0)
        self.plane2 = Aeroplane("TST2", "France", 180.0, 9000.0)

    def tearDown(self):
        """Удаляем временный файл после теста."""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
