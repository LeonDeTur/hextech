import json

with open(
        "app/grid_generator/services/constants/profiles.json",
        encoding="utf-8",
) as profiles_file:
    profiles = json.load(profiles_file)

prioc_objects_types = [
        "Медицинский комплекс",
        "Бизнес-кластер",
        "Пром объект",
        "Логистическо-складской комплекс",
        "Порт",
        "Кампус университетский",
        "Тур база",
    ]
