import json


with open(
        "app/prioc/services/constants/indicators_weights.json",
        "r",
        encoding="utf-8",
) as indicators_weights_file:
    INDICATORS_WEIGHTS = json.load(indicators_weights_file)

with open(
        "app/prioc/services/constants/object_indicators_min_val.json",
        "r",
        encoding="utf-8",
) as object_indicators_min_val_file:
    OBJECT_INDICATORS_MIN_VAL = json.load(object_indicators_min_val_file)

with open(
        "app/prioc/services/constants/positive_service_cleaning.json",
        "r",
        encoding="utf-8",
) as positive_service_cleaning_file:
    POSITIVE_SERVICE_CLEANING = json.load(positive_service_cleaning_file)

with open(
        "app/prioc/services/constants/negative_service_cleaning.json",
        "r",
        encoding="utf-8",
) as negative_service_cleaning_file:
    NEGATIVE_SERVICE_CLEANING = json.load(negative_service_cleaning_file)
