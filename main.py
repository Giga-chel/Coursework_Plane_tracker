import json
import os
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


class Storage(ABC):
    """Абстрактный класс (Коннектор) для хранилища данных."""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавить информацию о самолете."""
        pass

    @abstractmethod
    def update_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Обновить информацию о самолете."""
        pass

    @abstractmethod
    def get_aeroplanes(self, **kwargs) -> List[Aeroplane]:
        """Получить самолеты по критериям (фильтрация через kwargs)."""
        pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удалить информацию о самолете."""
        pass


class JSONSaver(Storage):
    """Класс для сохранения и чтения данных о самолетах в JSON-файл."""

    def __init__(self, filename: str = "data/aeroplanes.json"):
        dir_name = os.path.dirname(filename)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        self.filename = filename

    def _read_file(self) -> List[Dict]:
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def _write_file(self, data: List[Dict]) -> None:
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        data = self._read_file()
        data.append(aeroplane.to_dict())
        self._write_file(data)

    def update_aeroplane(self, aeroplane: Aeroplane) -> None:
        raise NotImplementedError("Обновление отдельных записей не поддерживается в JSON-формате.")

    def get_aeroplanes(self, **kwargs) -> List[Aeroplane]:
        data = self._read_file()
        results = []
        for item in data:
            match = all(item.get(k) == v for k, v in kwargs.items())
            if match:
                results.append(Aeroplane(**item))
        return results

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        data = self._read_file()
        target = aeroplane.to_dict()
        new_data = [
            item for item in data
            if not (item.get("callsign") == target["callsign"] and
                    item.get("origin_country") == target["origin_country"])
        ]
        self._write_file(new_data)

    def save_all_aeroplanes(self, aeroplanes: list[Aeroplane]) -> None:
        data = [aeroplane.to_dict() for aeroplane in aeroplanes]
        self._write_file(data)



def filter_aeroplanes(aeroplanes: List[Aeroplane], countries: List[str]) -> List[Aeroplane]:
    if not countries: return aeroplanes
    countries_lower = [c.lower() for c in countries]
    return [p for p in aeroplanes if p.origin_country.lower() in countries_lower]


def get_aeroplanes_by_altitude(aeroplanes: List[Aeroplane], altitude_range: str) -> List[Aeroplane]:
    if not altitude_range or '-' not in altitude_range: return aeroplanes
    try:
        parts = altitude_range.split('-')
        min_alt = float(parts[0].strip())
        max_alt = float(parts[1].strip())
        return [p for p in aeroplanes if min_alt <= p.altitude <= max_alt]
    except ValueError:
        print("Неверный формат диапазона высот.")
        return aeroplanes


def get_top_aeroplanes(aeroplanes: List[Aeroplane], n: int) -> List[Aeroplane]:
    return sorted(aeroplanes, reverse=True)[:n]


def print_aeroplanes(aeroplanes: List[Aeroplane]) -> None:
    if not aeroplanes:
        print("Самолеты по заданным критериям не найдены.\n")
        return
    print(f"{'Позывной':<15} | {'Страна рег.':<20} | {'Высота (м)':<15} | {'Скорость (м/с)':<15}")
    print("-" * 75)
    for p in aeroplanes:
        print(f"{p.callsign:<15} | {p.origin_country:<20} | {p.altitude:<15.2f} | {p.velocity:<15.2f}")
    print()


def user_interaction(api_fetcher: APIFetcher, saver: Storage) -> None:
    """Функция для взаимодействия с пользователем через консоль."""
    try:
        country = input("Введите название страны для поиска (на английском, например, Spain): ")
        if not country.strip():
            print("Название страны не может быть пустым.")
            return

        print(f"\nВыполняется запрос к API для страны {country}...")
        raw_data = api_fetcher.get_aeroplanes(country)
        aeroplanes = Aeroplane.cast_to_object_list(raw_data)

        if not aeroplanes:
            print("В данном воздушном пространстве самолетов не обнаружено (или достигнут лимит API).\n")
            return

        print(f"Найдено самолетов: {len(aeroplanes)}. Сохранение в файл...")
        saver.save_all_aeroplanes(aeroplanes)


        # --- Топ N по высоте ---
        top_n_input = input("\nВведите количество самолетов для Топ N по высоте (или Enter для пропуска): ")
        if top_n_input.strip():
            try:
                top_n = int(top_n_input)
                top_planes = get_top_aeroplanes(aeroplanes, top_n)
                print(f"\nТоп {top_n} самолетов по высоте в {country}:")
                print_aeroplanes(top_planes)
            except ValueError as e:
                print(f"Ошибка ввода: {e}")

        # --- Фильтр по стране регистрации ---
        filter_input = input("Введите страны регистрации для фильтрации через пробел (или Enter для пропуска): ")
        if filter_input.strip():
            filter_countries = filter_input.split()
            filtered = filter_aeroplanes(aeroplanes, filter_countries)
            print(f"\nСамолеты, зарегистрированные в {filter_countries}:")
            print_aeroplanes(filtered)

        # --- Фильтр по диапазону высот ---
        range_input = input("Введите диапазон высот (пример: 1000 - 10000) или Enter для пропуска: ")
        if range_input.strip():
            ranged = get_aeroplanes_by_altitude(aeroplanes, range_input)
            print(f"\nСамолеты в диапазоне высот {range_input}:")
            print_aeroplanes(ranged)

    except ValueError as e:
        print(f"Ошибка ввода: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Сетевая ошибка: {e}")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    api = AeroplanesAPI()
    json_saver = JSONSaver("aeroplanes_data.json")

    user_interaction(api, json_saver)