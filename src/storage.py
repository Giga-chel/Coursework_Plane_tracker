import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List

from src.models import Aeroplane


class Storage(ABC):
    """Абстрактный класс (Коннектор) для хранилища данных."""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавить информацию о самолете."""
        pass  # pragma: no cover

    @abstractmethod
    def update_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Обновить информацию о самолете."""
        pass  # pragma: no cover

    @abstractmethod
    def get_aeroplanes(self, **kwargs) -> List[Aeroplane]:
        """Получить самолеты по критериям (фильтрация через kwargs)."""
        pass  # pragma: no cover

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удалить информацию о самолете."""
        pass  # pragma: no cover

    @abstractmethod
    def save_all_aeroplanes(self, aeroplanes):
        """Сохранить всю информацию о самолетах."""
        pass  # pragma: no cover


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
        with open(self.filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def _write_file(self, data: List[Dict]) -> None:
        with open(self.filename, "w", encoding="utf-8") as f:
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
            item
            for item in data
            if not (
                item.get("callsign") == target["callsign"] and item.get("origin_country") == target["origin_country"]
            )
        ]
        self._write_file(new_data)

    def save_all_aeroplanes(self, aeroplanes: list[Aeroplane]) -> None:
        old_data = self._read_file()
        new_data = [aeroplane.to_dict() for aeroplane in aeroplanes]
        merged_dict = {item["callsign"]: item for item in (old_data + new_data)}
        self._write_file(list(merged_dict.values()))
