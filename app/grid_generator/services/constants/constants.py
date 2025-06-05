import json

with open(
        "app/grid_generator/services/constants/profiles.json",
        encoding="utf-8",
) as profiles_file:
    profiles = json.load(profiles_file)

with open(
        "app/grid_generator/services/constants/profile_efficiency.json",
        encoding="utf-8"
) as profile_efficiency_file:
    profile_efficiency = json.load(profile_efficiency_file)


prioc_objects_types = [
        "Медицинский комплекс",
        "Бизнес-кластер",
        "Пром объект",
        "Логистическо-складской комплекс",
        "Порт",
        "Кампус университетский",
        "Тур база",
    ]
