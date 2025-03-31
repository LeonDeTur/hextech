import asyncio
import json

import geopandas as gpd
from loguru import logger
from shapely.geometry import shape

from app.indicators_savior.indicators_savior_services.indicators_savior_api_service import indicators_savior_api_service
from .dto import IndicatorsDTO
from app.prioc.services import prioc_service
from app.grid_generator.services.potential_estimator import potential_estimator
from .indicators_savior_services.indicators_constants import objects_name_id_map


# ToDo rewrite whole service.
class IndicatorsSaviorService:

    @staticmethod
    async def post_potentials(
            potential_ter_estimation: dict,
            project_scenario_id: int
    ) -> None:

        potentials_id_map = await indicators_savior_api_service.get_name_id_map(269)
        async_task_list = []
        for key in potential_ter_estimation:
            value = potential_ter_estimation[key]
            indicator_id = potentials_id_map[key]
            first_to_put = {
                "indicator_id": indicator_id,
                "scenario_id": project_scenario_id,
                "territory_id": None,
                "hexagon_id": None,
                "value": value,
                "comment": None,
                "information_source": "hextech/potential",
                "properties": {}
            }
            async_task_list.append(indicators_savior_api_service.put_indicator(first_to_put))

        await asyncio.gather(*async_task_list)

    @staticmethod
    async def post_all(
            prioc_ter_estimation: dict,
            project_scenario_id: int,
    ) -> None:

        async_task_list = []
        for key in prioc_ter_estimation:
            value = prioc_ter_estimation[key]["estimation"]
            comment = ". ".join(prioc_ter_estimation[key]["interpretation"])
            indicator_id = objects_name_id_map[key]
            first_to_put = {
                "indicator_id": indicator_id,
                "scenario_id": project_scenario_id,
                "territory_id": None,
                "hexagon_id": None,
                "value": value,
                "comment": comment,
                "information_source": "hextech/prioc",
                "properties": {}
            }
            async_task_list.append(indicators_savior_api_service.put_indicator(first_to_put))

        await asyncio.gather(*async_task_list)

    async def save_potential(
            self,
            scenario_id: int,
            territory_id: int,
            territory: dict
    ) -> None:
        """
        Function calculates potential and saves result to db
        Args:
            scenario_id (int): id of scenario
            territory_id (int): id of region
            territory (dict): dict with territory geometry as FeatureCollection
        Returns:
            None
        """

        # indicators_values = []
        # indicators_values.append(await indicators_savior_api_service.get_ecological_evaluation(
        #     territory_id=territory_id,
        #     json_data=territory,
        # ))
        # indicators_values.append(await indicators_savior_api_service.get_transport_evaluation(
        #     territory_id=territory_id,
        #     json_data=territory,
        # ))
        # indicators_values.append(await indicators_savior_api_service.get_population_evaluation(
        #     territory_id=territory_id,
        #     json_data=territory,
        # ))
        # indicators_values.append(await indicators_savior_api_service.get_engineering_evaluation(
        #     territory_id=territory_id,
        #     json_data=territory,
        # ))
        # indicators_values.append(await indicators_savior_api_service.get_social_provision_evaluation(
        #     territory_id=territory_id,
        #     json_data=territory,
        # ))
        tasks = [
            indicators_savior_api_service.get_transport_evaluation(
                territory_id=territory_id,
                json_data=territory,
            ),
            indicators_savior_api_service.get_population_evaluation(
                territory_id=territory_id,
                json_data=territory,
            ),
            indicators_savior_api_service.get_engineering_evaluation(
                territory_id=territory_id,
                json_data=territory,
            ),
            indicators_savior_api_service.get_social_provision_evaluation(
                territory_id=territory_id,
                json_data=territory,
            ),
            indicators_savior_api_service.get_ecological_evaluation(
                territory_id=territory_id,
                json_data=territory,
            )
        ]
        indicators_values = await asyncio.gather(*tasks)
        indicators_dict = {}
        for indicator in indicators_values:
            for key, value in indicator.items():
                indicators_dict[key] = value
        result_dict = await potential_estimator.estimate_potentials_as_dict(indicators_dict)
        await self.post_potentials(result_dict, scenario_id)
        logger.info("Saved all potential indicators")

    @staticmethod
    async def save_recultivation(
            area: dict,
            base_scenario_id: int,
            target_scenario_id: int,
    ) -> None:
        """
        Save all recultivation results

        Args:
            area (dict): dict with geometry
            base_scenario_id (int): id of base scenario
            target_scenario_id (int): id of target scenario
        Returns:
            None
        """

        recultivation_data = await indicators_savior_api_service.get_recultivation_marks(
            area=area,
            base_scenario_id=base_scenario_id,
            target_scenario_id=target_scenario_id
        )

        time_estimation = {
            "indicator_id": 299,
            "scenario_id": target_scenario_id,
            "territory_id": None,
            "hexagon_id": None,
            "value": recultivation_data["data"]["recultivation"]["total"]["timeOfWork"],
            "comment": None,
            "information_source": "Redevelopment Generation",
            "properties": {}
        }

        money_estimation = {
                "indicator_id": 298,
                "scenario_id": target_scenario_id,
                "territory_id": None,
                "hexagon_id": None,
                "value": recultivation_data["data"]["recultivation"]["total"]["costOfWork"],
                "comment": None,
                "information_source": "Redevelopment Generation",
                "properties": {}
            }

        task_list = [
            indicators_savior_api_service.put_indicator(time_estimation),
            indicators_savior_api_service.put_indicator(money_estimation)
            ]
        await asyncio.gather(*task_list)
        logger.info("Saved all recultivation indicators")

    @staticmethod
    async def save_all_landuse(
            project_scenario_id: int,
    ) -> None:
        """
        Function puts all landuse data in urban_db
        Args:
            project_scenario_id: id of project scenario
        Returns:
            None
        """

        landuse_map = await indicators_savior_api_service.get_landuse_ids_names_map()
        landuse_estimation = await indicators_savior_api_service.get_landuse_estimation(
            project_scenario_id,
        )
        async_task_list = []
        for key in landuse_estimation:
            first_to_put = {
                "indicator_id": int(landuse_map[key]),
                "scenario_id": project_scenario_id,
                "territory_id": None,
                "hexagon_id": None,
                "value": float(landuse_estimation[key]),
                "comment": None,
                "information_source": "landuse_det",
                "properties": {}
            }
            async_task_list.append(indicators_savior_api_service.put_indicator(first_to_put))

        await asyncio.gather(*async_task_list)
        logger.info("Saved all landuse indicators")

    async def save_prioc_evaluations(
            self,
            scenario_id: int,
            territory_id: int,
            territory: dict
    ) -> None:
        """
        Function calculates parameters and saves result to db
        Args:
            scenario_id (int): id of scenario
            territory_id (int): id of region
            territory (dict): dict with territory geometry
        Returns:
            None
        """

        evaluations = await prioc_service.get_territory_estimation(
            territory=territory,
            territory_id=territory_id,
        )
        await self.post_all(evaluations, scenario_id)
        logger.info("Saved prioc evaluations")

    async def save_all_indicators(
            self,
            save_params: IndicatorsDTO
    ):
        """
        Function calculates and save all indicators to db
        Args:
            save_params (IndicatorsDTO): request params
        Returns:
            None
        """

        territory_data = await indicators_savior_api_service.get_project_data(save_params.project_id)
        territory = gpd.GeoDataFrame(geometry=[shape(territory_data["geometry"])], crs=4326)
        territory_geojson = json.loads(territory.to_json())
        territory_id = territory_data["project"]["region"]["id"]
        base_scenario = await indicators_savior_api_service.get_base_scenario_by_project(save_params.project_id)
        extract_list = [
            indicators_savior_api_service.save_net_indicators(
                territory=territory,
                region_id=territory_id,
                project_scenario_id=save_params.scenario_id
            ),
            indicators_savior_api_service.save_eco_frame_estimation(
                territory=territory_data["geometry"],
                region_id=territory_id,
                project_scenario_id=save_params.scenario_id,
            ),
            self.save_all_landuse(save_params.scenario_id),
            self.save_prioc_evaluations(
                scenario_id=save_params.scenario_id,
                territory_id=territory_id,
                territory=territory_data["geometry"],
            ),
            self.save_recultivation(
                area=territory_data["geometry"],
                base_scenario_id=base_scenario,
                target_scenario_id=save_params.scenario_id
            ),
            self.save_potential(
            scenario_id=save_params.scenario_id,
            territory_id=territory_id,
            territory=territory_geojson
            )
        ]
        await asyncio.gather(*extract_list)
        # await indicators_savior_api_service.save_net_indicators(
        #     territory=territory,
        #     region_id=territory_id,
        #     project_scenario_id=save_params.scenario_id
        # )
        # await self.save_all_landuse(save_params.scenario_id)
        # await self.save_prioc_evaluations(
        #         scenario_id=save_params.scenario_id,
        #         territory_id=territory_id,
        #         territory=territory_data["geometry"],
        #     )
        # if save_params.scenario_id != base_scenario:
        #     await self.save_recultivation(
        #             area=territory_data["geometry"],
        #             base_scenario_id=base_scenario,
        #             target_scenario_id=save_params.scenario_id
        #         )
        # await self.save_potential(
        #     scenario_id=save_params.scenario_id,
        #     territory_id=territory_id,
        #     territory=territory_geojson
        #     )
        # await indicators_savior_api_service.save_eco_frame_estimation(
        #     territory=territory_data["geometry"],
        #     region_id=territory_id,
        #     project_scenario_id=save_params.scenario_id,
        # )
        # await self.save_potential(
        #     scenario_id=save_params.scenario_id,
        #     territory_id=territory_id,
        #     territory=territory_geojson
        # )
        logger.info(f"Finished saving all indicators with params {save_params.__dict__}")
        return {"msg": "Successfully saved all indicators"}



indicators_savior_service = IndicatorsSaviorService()
