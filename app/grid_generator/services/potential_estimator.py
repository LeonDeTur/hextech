import geopandas as gpd
from loguru import logger

from .constants import profiles


class PotentialEstimator:

    @staticmethod
    async def estimate_potential(
            indicators_values: dict[str, int]
    ) -> list[int]:
        """
        Function estimates potential for territory based on indicators

        Args:
            indicators_values: dictionary of indicators values

        Returns:
            int: estimated value of potential
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
            cur_potential = await self.estimate_potential(row.to_dict())
            result_list.append(cur_potential)

        columns = list(profiles.keys())
        hexes[columns] = result_list
        logger.info(f"Finished potential estimation with {len(hexes)} hexes")

        return hexes


potential_estimator = PotentialEstimator()
