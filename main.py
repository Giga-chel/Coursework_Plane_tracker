import requests
from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional

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

        response = self.session.get(url, params=params)
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

        response = self.session.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Ошибка API OpenSky: {response.status_code}")
        data = response.json()
        return data.get("states", [])


class Aeroplane:
    """Класс, представляющий самолет."""

    def __init__(self, callsign: str, origin_country: str, velocity: float, altitude: float, on_ground: bool = False):
        self.callsign = callsign
        self.origin_country = origin_country
        self.velocity = velocity
        self.altitude = altitude
        self.on_ground = on_ground

    @property
    def callsign(self) -> str:
        return self._callsign

    @callsign.setter
    def callsign(self, value: Optional[str]):
        self._callsign = str(value).strip() if value else "N/A"

    @property
    def origin_country(self) -> str:
        return self._origin_country

    @origin_country.setter
    def origin_country(self, value: Optional[str]):
        self._origin_country = str(value).strip() if value else "Unknown"

    @property
    def velocity(self) -> float:
        return self._velocity

    @velocity.setter
    def velocity(self, value: Optional[float]):
        self._velocity = float(value) if value is not None else 0.0

    @property
    def altitude(self) -> float:
        return self._altitude

    @altitude.setter
    def altitude(self, value: Optional[float]):
        self._altitude = float(value) if value is not None else 0.0

    @property
    def on_ground(self) -> bool:
        return self._on_ground

    @on_ground.setter
    def on_ground(self, value: bool):
        self._on_ground = bool(value)

    def is_higher_than(self, other: 'Aeroplane') -> bool:
        return self.altitude > other.altitude

    def is_faster_than(self, other: 'Aeroplane') -> bool:
        return self.velocity > other.velocity

    def __lt__(self, other: 'Aeroplane') -> bool:
        return self.altitude < other.altitude

    def __repr__(self):
        return f"Aeroplane(callsign={self.callsign}, country={self.origin_country}, alt={self.altitude})"

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация объекта в словарь для сохранения."""
        return {
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "velocity": self.velocity,
            "altitude": self.altitude,
            "on_ground": self.on_ground
        }

    @classmethod
    def cast_to_object_list(cls, raw_data: List[list]) -> List['Aeroplane']:
        """Превращает ответ API в список объектов Aeroplane."""
        aeroplanes = []
        for state in raw_data:
            try:
                callsign = state[1]
                origin_country = state[2]
                velocity = state[9]
                altitude = state[13] if state[13] is not None else state[7]
                on_ground = state[8]
            except IndexError:
                continue

            aeroplanes.append(cls(callsign, origin_country, velocity, altitude, on_ground))
        return aeroplanes
