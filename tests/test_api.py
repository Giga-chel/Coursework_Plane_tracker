import unittest
from unittest.mock import MagicMock, patch

from src.api import AeroplanesAPI


class TestAeroplanesAPI(unittest.TestCase):

    @patch("src.api.AeroplanesAPI.get_country_bounding_box")
    @patch("src.api.requests.Session")
    def test_get_aeroplanes_success(self, mock_session_class, mock_bb_method):
        mock_bb_method.return_value = (0.0, 0.0, 0.0, 0.0)
        fake_response = MagicMock()
        fake_response.json.return_value = {
            "states": [["TST1", "France", 0, 0, 0, 0, 0, 0, False, 150.5, 0, 0, 0, 8000.0]]
        }
        fake_response.status_code = 200
        mock_session_class.return_value.get.return_value = fake_response

        api = AeroplanesAPI()
        result = api.get_aeroplanes("France")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "TST1")
