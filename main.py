import requests
from src.api import APIFetcher, AeroplanesAPI
from src.models import Aeroplane
from src.storage import Storage, JSONSaver
from src.utils import filter_aeroplanes, get_aeroplanes_by_altitude, get_top_aeroplanes, print_aeroplanes


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