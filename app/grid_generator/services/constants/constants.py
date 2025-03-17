import json

with open(
        "app/grid_generator/services/constants/profiles.json",
        encoding="utf-8",
) as profiles_file:
    profiles = json.load(profiles_file)
