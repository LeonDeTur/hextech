from collections import ChainMap

import geopandas as gpd
from loguru import logger

from .constants import profiles, profile_efficiency


class PotentialEstimator:

    @staticmethod
    async def estimate_potential(
            indicators_values: dict[str, int] | ChainMap,
    ) -> list[int]:
        """
        Function estimates potential for territory based on indicators

        Args:
            indicators_values: dictionary of indicators values

        Returns:
            list[int]: estimated value of potential
        """

        result = [
            sum(
                [
                    True for key, value in indicators_values.items()
                    if value >= profiles[profile_name]["Критерии"][key]
                ]
            ) for profile_name in profiles.keys()
        ]
        return result

    @staticmethod
    async def estimate_potentials_as_dict(
            indicators_values: dict,
    ):

        result = {
            profile_name: sum(
                [
                    value >= profiles[profile_name]["Критерии"][key]
                    for key, value in indicators_values.items()
                ]
            ) for profile_name in profiles.keys()
        }

        return result

    @staticmethod
    async def estimate_potentials_weights(potential_min_values: dict) -> dict[str, dict[str, float]]:
        """
        Function estimates potential weights for territory based on indicators values
        Args:
            potential_min_values: dictionary of indicators values with min values
        Returns:
            dict[str, float]: estimated weight value for each potential
        """

        weights = {}
        for profile in profiles.keys():
            try:
                weights[profile] = {
                    indicator_name: {
                        "weight": profiles[profile]["Критерии"][indicator_name] / sum([profiles[profile]["Критерии"][i] for i in profiles[profile]["Критерии"].keys()]),
                        "min_value": potential_min_values[profile]["Критерии"][indicator_name]
                    } for indicator_name in profiles[profile]["Критерии"].keys()
                }
            except Exception as e:
                print(e.__str__())

        return weights

    #ToDo add fine for zone changes
    @staticmethod
    async def estimate_expenses(
            profiles_weights: dict,
            indicators_values: dict[str, int] | ChainMap
    ) -> dict[str, float]:
        """
        Function estimates expenses for territory based on indicators values and weights

        Args:
            profiles_weights: dictionary of profiles weights
            indicators_values: dictionary of indicators values

        Returns:
            list[int]: estimated value of expenses
        """

        result = {}
        for key, value in profiles_weights.items():
            estimation = sum(
                [
                    (value[i]["min_value"] - indicators_values[i]) * value[i]["weight"] for i in value.keys()
                ]
            )
            result[key] = estimation
        return result

    async def calc_balanced_potential(
            self,
            indicators_values: dict[str, int] | ChainMap,
            as_dict: bool = True,
    ) -> dict[str, float] | list[float]:
        """
        Function calculates balanced potential for territory based on indicators values
        Args:
            indicators_values: dictionary of indicators values
            as_dict: if True, returns dict with potential values, otherwise returns list
        Returns:
            dict[str, float] | list[float]: balanced potential values
        """

        res = {}
        potentials = await self.estimate_potentials_as_dict(indicators_values)
        potential_weights = await self.estimate_potentials_weights(profiles)
        potential_expenses = await self.estimate_expenses(potential_weights, indicators_values)
        for key in potentials.keys():
            res[key] = profile_efficiency[key] - potential_expenses[key]
        if as_dict:
            return res
        return [i for i in res.values()]

    async def estimate_potentials(
            self,
            hexes: gpd.GeoDataFrame
    ) -> gpd.GeoDataFrame:
        logger.info(f"Started potential estimation with {len(hexes)} hexes")
        result_list = []
        drop_list = [column for column in [
            "geometry", "hexagon_id", "properties"] if column in list(hexes.columns)
                     ]
        hexes_df = hexes.drop(columns=drop_list)
        for index, row in hexes_df.iterrows():
            cur_potential = await self.calc_balanced_potential(row.to_dict(), as_dict=False)
            result_list.append(cur_potential)

        columns = list(profiles.keys())
        hexes[columns] = result_list
        logger.info(f"Finished potential estimation with {len(hexes)} hexes")

        return hexes


potential_estimator = PotentialEstimator()
