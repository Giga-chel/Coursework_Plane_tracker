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

    def test_save_all_merges_and_updates(self):
        """Тест добавления и полного сохранения."""
        self.saver.add_aeroplane(self.plane1)
        data = self.saver.get_aeroplanes()
        self.assertEqual(len(data), 1)

        self.plane1_updated = Aeroplane("TST1", "Germany", 120.0, 7500.0)

        self.saver.save_all_aeroplanes([self.plane1_updated, self.plane2])
        data = self.saver.get_aeroplanes()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0].altitude, 7500.0)
        self.assertEqual(data[0].callsign, "TST1")

    def test_get_aeroplanes_with_filters(self):
        """Тест получения данных по критериям (kwargs)."""
        self.saver.save_all_aeroplanes([self.plane1, self.plane2])
        filtered = self.saver.get_aeroplanes(origin_country="Germany")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].callsign, "TST1")

    def test_delete_aeroplane(self):
        """Тест удаления самолета из хранилища."""
        self.saver.save_all_aeroplanes([self.plane1, self.plane2])
        self.saver.delete_aeroplane(self.plane1)

        data = self.saver.get_aeroplanes()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].callsign, "TST2")

    def test_update_stub(self):
        """Тест проверки заглушки для метода update."""
        with self.assertRaises(NotImplementedError):
            self.saver.update_aeroplane(self.plane1)


if __name__ == '__main__':
    unittest.main()