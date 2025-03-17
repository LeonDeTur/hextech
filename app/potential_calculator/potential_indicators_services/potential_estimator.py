# import geopandas as gpd
# from loguru import logger
#
# from .constants import profiles
#
#
# class PotentialEstimator:
#
#     @staticmethod
#     async def estimate_potentials(
#             territory: gpd.GeoDataFrame
#     ) -> list[int]:
#         """
#         Function estimates potential for territory based on indicators
#
#         Args:
#             territory (gpd.GeoDataFrame): dictionary of indicators values
#
#         Returns:
#             int: estimated value of potential
#         """
#
#         exclude_list = ["geometry"]
#         df_without_geometry = territory.drop(columns=exclude_list)
#         indicators_values = df_without_geometry.iloc[0].to_dict()
#         result = [
#             sum(
#                 [
#                     True for key, value in indicators_values.items()
#                     if value >= profiles.json[profile_name]["Критерии"][key]
#                 ]
#             ) for profile_name in profiles.json.keys()
#         ]
#         return result
#
#
# potential_estimator = PotentialEstimator()
