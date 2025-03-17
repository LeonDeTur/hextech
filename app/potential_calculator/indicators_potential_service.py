# import json
#
# import geopandas as gpd
# from shapely.geometry import shape
#
# from .potential_indicators_services.potentials_api_extractor import potential_api_extractor
# from .dto.indicators_dto import IndicatorsDTO
#
#
# class IndicatorsPotentialService:
#
#     @staticmethod
#     async def estimate_territory(self, params: IndicatorsDTO):
#
#         territory_gdf = gpd.GeoDataFrame(shape(params.territory.__dict__), crs=4326)
#         territory_json = json.loads(territory_gdf.to_json())
#         indicators = await potential_api_extractor.get_all_indicators(
#             territory_json=territory_json,
#             region_id=params.region_id,
#         )
#         for i in
#
