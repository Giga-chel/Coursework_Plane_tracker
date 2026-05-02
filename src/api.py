import requests
from abc import ABC, abstractmethod
from typing import List

class APIFetcher(ABC):
    """Абстрактный класс для работы с API."""

    @abstractmethod
    def get_country_bounding_box(self, country: str) -> tuple:
        """Получить координаты (bounding box) страны."""
        pass

    @abstractmethod
    def get_aeroplanes(self, country: str) -> List[list]:
        """Получить сырые данные о самолетах в воздушном пространстве страны."""
        pass


class AeroplanesAPI(APIFetcher):
    """Класс для работы с API Nominatim и OpenSky Network."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AeroplaneTracker/1.0"})

    def get_country_bounding_box(self, country: str) -> tuple:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": country, "format": "json", "limit": 1}

        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            raise ValueError(f"Страна '{country}' не найдена.")

        bb = data[0]["boundingbox"]
        return float(bb[0]), float(bb[1]), float(bb[2]), float(bb[3])

    def get_aeroplanes(self, country: str) -> List[list]:
        south, north, west, east = self.get_country_bounding_box(country)

        url = "https://opensky-network.org/api/states/all"
        params = {
            "lamin": south,
            "lamax": north,
            "lomin": west,
            "lomax": east
        }

        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("states", [])
