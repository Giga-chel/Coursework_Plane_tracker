from operator import attrgetter
from typing import List

from src.models import Aeroplane


def filter_aeroplanes(aeroplanes: List[Aeroplane], countries: List[str]) -> List[Aeroplane]:
    if not countries:
        return aeroplanes
    countries_lower = [c.lower() for c in countries]
    return [p for p in aeroplanes if p.origin_country.lower() in countries_lower]


def get_aeroplanes_by_altitude(aeroplanes: List[Aeroplane], altitude_range: str) -> List[Aeroplane]:
    if not altitude_range or "-" not in altitude_range:
        return aeroplanes
    try:
        parts = altitude_range.split("-")
        min_alt_plane, max_alt_plane = sorted([float(ap.strip()) for ap in parts])
        return [p for p in aeroplanes if min_alt_plane <= p.altitude <= max_alt_plane]
    except ValueError:
        print("Неверный формат диапазона высот.")
        return aeroplanes


def get_top_aeroplanes(aeroplanes: List[Aeroplane], n: int, sort_by: str = "altitude") -> List[Aeroplane]:
    key_func = attrgetter(sort_by)
    return sorted(aeroplanes, key=key_func, reverse=True)[:n]


def print_aeroplanes(aeroplanes: List[Aeroplane]) -> None:
    if not aeroplanes:
        print("Самолеты по заданным критериям не найдены.\n")
        return
    print(f"{'Позывной':<15} | {'Страна рег.':<20} | {'Высота (м)':<15} | {'Скорость (м/с)':<15}")
    print("-" * 75)
    for p in aeroplanes:
        print(f"{p.callsign:<15} | {p.origin_country:<20} | {p.altitude:<15.2f} | {p.velocity:<15.2f}")
    print()
