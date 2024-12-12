import geopandas as gpd

from .constants import INDICATORS_WEIGHTS, OBJECT_INDICATORS_MIN_VAL


class TerritoryEstimator:
    """
    Class for evaluating possible priority objects allocation
    """

    @staticmethod
    async def estimate_territory(
            territory_hexagons: gpd.GeoDataFrame,
    ):
        """
        Function estimates possible priority objects allocation for territory

        Args:
            territory_hexagons (GeoDataFrame): hexagons with indicators within provided territory

        Returns:
            dict: dict with estimated values and interpretation
        """

        async def interpret_value(
                actual: int,
                target: int,
                indicator_name: str
        ) -> str:
            if actual < target:
                return f"Слабый показатель: {indicator_name.lower()}"
            else:
                return f"Хороший показатель: {indicator_name.lower()}"

        indicators = territory_hexagons.drop(columns=['geometry']).mean().to_dict()

        result_dict = {}

        for key in INDICATORS_WEIGHTS.json.keys():
            result_dict[key] = {}
            interpretations = []
            current_object_indicators_min_val = OBJECT_INDICATORS_MIN_VAL.json[key]
            ranks = INDICATORS_WEIGHTS.json[key]
            n = len(ranks)
            total_score = 0
            for indicator, rank in ranks.items():
                if ranks[indicator] > 3:
                    current_interpretation = await interpret_value(
                        actual=indicators[indicator],
                        target=current_object_indicators_min_val[indicator],
                        indicator_name=indicator,
                    )
                    interpretations.append(current_interpretation)
                denominator = sum([n - rank + 1 for rank in ranks.values()])
                weight = (n - rank + 1) / denominator
                score = (indicators[indicator] - current_object_indicators_min_val[indicator]) * weight
                total_score += score
            result_dict[key]["estimation"] = round(total_score, 2)
            result_dict[key]["interpretation"] = interpretations

        return result_dict


territory_estimator = TerritoryEstimator()
