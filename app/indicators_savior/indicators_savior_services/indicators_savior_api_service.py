import asyncio
import json

import aiohttp
import geopandas as gpd

from app.common import config
from app.common.api_handler.api_handler import (
    urban_api_handler,
    eco_frame_api_handler,
    townsnet_api_handler,
    pop_frame_api_handler,
    transport_frame_api_handler
)


class IndicatorsSaviorApiService:

    def __init__(self):
        self.headers = {"Authorization" :f'Bearer {config.get("ACCESS_TOKEN")}'}

    async def put_indicator(
            self,
            json_data: dict
    ) -> None:
        """
        Function extracts put indicators query with params

        Args:
            json_data (dict): indicators_data_to_post

        Returns:
            None
        """

        async with aiohttp.ClientSession() as session:
            await urban_api_handler.put(
                session=session,
                extra_url="/api/v1/scenarios/indicators_values",
                headers=self.headers,
                data=json_data
            )

    async def save_net_indicators(
            self,
            territory: gpd.GeoDataFrame,
            region_id: int,
            project_scenario_id: int
    ) -> None:
        """
        Function extracts save functions from towns, pop and transport frames

        Args:
            territory (gpd.GeoDataFrame): The territory to be saved
            region_id: (int): region_id where project is located
            project_scenario_id: (int): project_scenario_id as it is in db

        Returns:
            dict with indicators group names and save results
        """

        json_territory = json.loads(territory.to_json())
        tasks = [
            pop_frame_api_handler.post(
                extra_url="/PopFrame/save_popframe_evaluation",
                params={
                    "region_id": region_id,
                    "project_scenario_id": project_scenario_id,
                },
                headers=self.headers,
                data=json_territory,
            ),
            transport_frame_api_handler.post(
                extra_url=f"/{region_id}/transport_criteria_project",
                params={
                    "region_id": region_id,
                    "project_scenario_id": project_scenario_id,
                },
                headers=self.headers,
                data=json_territory,
            ),
            townsnet_api_handler.post(
                extra_url=f"/provision/{region_id}/evaluate_project",
                params={
                    "project_scenario_id": project_scenario_id,
                },
                headers=self.headers,
                data=json_territory,
            ),
            townsnet_api_handler.post(
                extra_url=f"/engineering/{region_id}/evaluate_project",
                params={
                    "project_scenario_id": project_scenario_id,
                },
                headers=self.headers,
                data=json_territory,
            )
        ]

        await asyncio.gather(*tasks)

    async def save_eco_frame_estimation(
            self,
            territory: dict[str, str | list],
            region_id: int,
            project_scenario_id: int,
    ) -> None:
        """
        Function counts and puts indicators data for ecoframe estimation

        Args:
            territory (dict[str, str | list]): geometry dict
            region_id (int): region_id where project is located
            project_scenario_id: (int): project_scenario_id as it is in db
        """

        data_to_post = {"geometry": territory}

        eco_marks = await eco_frame_api_handler.post(
            extra_url=f"/api/v1/ecodonut/{region_id}/mark",
            data=data_to_post,
        )
        first_to_put = {
            "indicator_id": 194,
            "scenario_id": project_scenario_id,
            "territory_id": 1,
            "hexagon_id": None,
            "value": eco_marks["relative_mark"],
            "comment": eco_marks["relative_mark_description"],
            "information_source": "ecoframe",
            "properties": {}
        }
        second_to_put = {
            "indicator_id": 199,
            "scenario_id": project_scenario_id,
            "territory_id": 1,
            "hexagon_id": None,
            "value": eco_marks["absolute_mark"],
            "comment": eco_marks["absolute_mark_description"],
            "information_source": "ecoframe",
            "properties": {}
        }

        for put_data in (first_to_put, second_to_put):
            async with aiohttp.ClientSession() as session:
                await urban_api_handler.put(
                    session=session,
                    extra_url=f"/api/v1/scenarios/indicators_values",
                    headers=self.headers,
                    data=put_data,
                )


indicators_savior_api_service = IndicatorsSaviorApiService()
