# from loguru import logger
#
# from app.common.api_handler.task_api_wrapper import tasks_api_handler
# from app.common.api_handler.api_handler import (
#     urban_api_handler,
#     eco_frame_api_handler,
#     townsnet_api_handler,
#     pop_frame_api_handler,
#     transport_frame_api_handler
# )
#
# class IndicatorsPotentialService:
#
#     def __init__(self):
#         self.headers = {}
#         self.urban_extractor = urban_api_handler
#         self.eco_frame_extractor = eco_frame_api_handler
#         self.townsnet_extractor = townsnet_api_handler
#         self.pop_frame_extractor = pop_frame_api_handler
#         self.transport_frame_extractor = transport_frame_api_handler
#
#
#     async def get_social_provision_evaluation(
#             self,
#             territory_id: int,
#             json_data: dict | list
#     ):
#         """
#         Function retrieves evaluation for social provision
#         Args:
#             territory_id (int): Territory ID
#             json_data (dict): Data for evaluation
#
#         Returns:
#             dict | list: Evaluated data
#         """
#
#         logger.info(f"Started provision extraction for {len(json_data['features'])} territories")
#         response = await self.townsnet_extractor.post(
#             extra_url=f"/provision/{territory_id}/get_evaluation",
#             data=json_data,
#             headers=self.headers
#         )
#
#         return {"Социальное обеспечение": response}
#
#     async def get_engineering_evaluation(
#             self,
#             territory_id: int,
#             json_data: dict | list
#     ) -> dict | list:
#         """
#         Function retrieves evaluation for engineering
#         Args:
#             territory_id (int): Territory ID
#             json_data (dict): Data for evaluation
#
#         Returns:
#             dict | list: Evaluated data
#         """
#
#         response = await self.townsnet_extractor.post(
#             extra_url=f"/engineering/{territory_id}/evaluate_geojson",
#             data=json_data,
#             headers=self.headers
#         )
#         return {"Обеспечение инженерной инфраструктурой": response}
#
#     async def get_transport_evaluation(
#             self,
#             territory_id: int,
#             json_data: dict | list
#     ) -> dict | list:
#         """
#         Function retrieves transport frame
#         Args:
#             territory_id (int): Territory ID
#             json_data (dict): Data for evaluation
#
#         Returns:
#             dict | list: Transport frame
#         """
#
#         response = await self.transport_frame_extractor.post(
#             extra_url=f"/{territory_id}/transport_criteria",
#             data=json_data
#         )
#         return {"Транспортное обеспечение": response}
#
#     async def get_ecological_evaluation(
#             self,
#             territory_id: int,
#             json_data: dict | list
#     ) -> dict | list:
#         """
#         Function retrieves evaluation for ecological
#         Args:
#             territory_id (int): Territory ID
#             json_data (dict): Data for evaluation
#
#         Returns:
#             dict | list: Evaluated data
#         """
#
#         eco_feature_collection = {"feature_collection": json_data}
#         response = await self.eco_frame_extractor.post(
#             extra_url=f"/ecodonut/{territory_id}/mark",
#             data=eco_feature_collection
#         )
#         result = [item["relative_mark"] for item in response]
#         return {"Экологическая ситуация": result}
#
#     async def get_population_evaluation(
#             self,
#             territory_id: int,
#             json_data: dict | list
#     ) -> dict | list:
#         """
#         Function retrieves evaluation for population
#         Args:
#             territory_id (int): Territory ID
#             json_data (dict): Data for evaluation
#
#         Returns:
#             dict | list: Evaluated data
#         """
#
#         response = await self.pop_frame_extractor.post(
#             extra_url=f"/population/get_population_criterion_score",
#             params={"region_id": territory_id},
#             data=json_data,
#             headers=self.headers
#         )
#         return {"Население": response}
#
#     async def get_all_indicators(
#             self,
#             territory: dict,
#             region_id: int
#     ) -> list[dict]:
#
#         task_list = [
#             self.get_ecological_evaluation(territory_id=region_id, json_data=territory),
#             self.get_population_evaluation(territory_id=region_id, json_data=territory),
#             self.get_transport_evaluation(territory_id=region_id, json_data=territory),
#             self.get_engineering_evaluation(territory_id=region_id, json_data=territory),
#             self.get_transport_evaluation(territory_id=region_id, json_data=territory)
#         ]
#
#         results = tasks_api_handler.extract_requests_to_several_urls(
#             task_list,
#             territory_id=region_id,
#             geojson_data=territory,
#         )
#
#         return results
#
#
# potential_api_extractor = IndicatorsPotentialService()
