import asyncio

import geopandas as gpd
from loguru import logger
from shapely.geometry import shape

from app.indicators_savior.indicators_savior_services.indicators_savior_api_service import indicators_savior_api_service
from .dto import IndicatorsDTO
from app.prioc.services import prioc_service
from .indicators_savior_services.indicators_constants import objects_name_id_map


# ToDo rewrite whole service.
class IndicatorsSaviorService:

    @staticmethod
    async def post_all(
            prioc_ter_estimation: dict,
            project_scenario_id: int,
    ):

        async_task_list = []
        for key in prioc_ter_estimation:
            value = prioc_ter_estimation[key]["estimation"]
            comment = ". ".join(prioc_ter_estimation[key]["interpretation"])
            indicator_id = objects_name_id_map[key]
            first_to_put = {
                "indicator_id": indicator_id,
                "scenario_id": project_scenario_id,
                "territory_id": 1,
                "hexagon_id": None,
                "value": value,
                "comment": comment,
                "information_source": "hextech/prioc",
                "properties": {}
            }
            async_task_list.append(indicators_savior_api_service.put_indicator(first_to_put))

        await asyncio.gather(*async_task_list)

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

        territory = gpd.GeoDataFrame(geometry=[shape(save_params.territory.__dict__)], crs=4326)
        await indicators_savior_api_service.save_net_indicators(
            territory=territory,
            region_id=save_params.territory_id,
            project_scenario_id=save_params.scenario_id,
        )
        await indicators_savior_api_service.save_eco_frame_estimation(
            territory=save_params.territory.__dict__,
            region_id=save_params.territory_id,
            project_scenario_id=save_params.scenario_id,
        )
        evaluations = await prioc_service.prioc_service.get_territory_estimation(save_params)
        await self.post_all(evaluations, save_params.scenario_id)
        logger.info(f"Finished saving all indicators with scenario id {save_params.scenario_id}")
        return {"msg": "Successfully saved all indicators"}


indicators_savior_service = IndicatorsSaviorService()
