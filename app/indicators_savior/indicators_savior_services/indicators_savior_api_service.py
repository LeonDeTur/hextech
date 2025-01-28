import asyncio
import json

import aiohttp
import geopandas as gpd
import pandas as pd

from app.common import config
from app.common.api_handler.api_handler import (
    urban_api_handler,
    eco_frame_api_handler,
    townsnet_api_handler,
    pop_frame_api_handler,
    transport_frame_api_handler,
    landuse_det_api_handler
)
from .recaltivation_api_handler import recultivation_api_handler


class IndicatorsSaviorApiService:

    def __init__(self):
        self.headers = {"Authorization" :f'Bearer {config.get("ACCESS_TOKEN")}'}

    async def get_base_scenario_by_project(
            self,
            project_id: int
    ) -> int:
        """
        Function returns base scenario for project

        Args:
            project_id (int): id of project
        Returns:
            int: base scenario
        """

        base_scenario_data = await urban_api_handler.get(
            extra_url=f"/api/v1/projects/{project_id}/scenarios",
            headers=self.headers,
        )
        base_scenario_df = pd.DataFrame(base_scenario_data)
        base_scenario_id = int(base_scenario_df[base_scenario_df["is_based"]]["scenario_id"].iloc[0])
        return base_scenario_id

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
            pop_frame_api_handler.put(
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
            townsnet_api_handler.put(
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
            "territory_id": None,
            "hexagon_id": None,
            "value": eco_marks["relative_mark"],
            "comment": eco_marks["relative_mark_description"],
            "information_source": "ecoframe",
            "properties": {}
        }
        second_to_put = {
            "indicator_id": 199,
            "scenario_id": project_scenario_id,
            "territory_id": None,
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

    @staticmethod
    async def get_landuse_ids_names_map() -> dict:
        """
        Function extracgts landuse indicators data

        Returns:
            dict with landuse indicators data
        """

        result = {}
        response = await urban_api_handler.get(
            extra_url="/api/v1/indicators_by_parent",
            params={"parent_id": 16}
        )
        for indicator in response:
            result[indicator["name_full"]] = indicator["indicator_id"]
        response = await urban_api_handler.get(
            "/api/v1/indicators/16"
        )
        result["name_full"] = response["indicator_id"]
        return result

    @staticmethod
    async def get_landuse_estimation(
            scenario_id: int,
        ):
        """
        Function extracts landuse estimation for provided scenario and territory

        Args:
            scenario_id (int): scenario id from urban_db

        Returns:
            dict with landuse indicators data
        """

        response = await landuse_det_api_handler.get(
            extra_url=f"/api/projects/{scenario_id}/landuse_percentages",
        )
        return response

    async def get_project_data(self, project_id: int) -> list | dict:
        """
        Function extracts project data for given project id

        Args:
            project_id (int): project id from urban_db
        Returns:
            dict with project data
        """

        response = await urban_api_handler.get(
            extra_url=f"/api/v1/projects/{project_id}/territory",
            headers=self.headers
        )
        return response

    async def get_recultivation_marks(
        self,
        area: dict,
        territory_id: int,
        base_scenario_id: int,
        target_scenario_id: int,
    ) -> None:
        """
        Function calculate and get recultivation marks to urban api

        Args:
            area (dict): area geometry from urban_db
            base_scenario_id (int): base scenario id from urban_db
            target_scenario_id (int): target scenario id from urban_db
        Returns:
            None
        """

        async def _form_source_params(sources: list[dict]) -> dict:
            source_names = [i["source"] for i in sources]
            source_data_df = pd.DataFrame(sources)
            if "PZZ" in source_names:
                return source_data_df.loc[
                    source_data_df[source_data_df["source"] == "PZZ"]["year"].idxmax()
                ].to_dict()
            elif "OSM" in source_names:
                return source_data_df.loc[
                    source_data_df[source_data_df["source"] == "OSM"]["year"].idxmax()
                ].to_dict()
            else:
                return source_data_df.loc[
                    source_data_df[source_data_df["source"] == "User"]["year"].idxmax()
                ].to_dict()

        async def _map_matrix_names(matrix_data: dict[str, list]) -> dict[str, list]:
            renamed_recultivation_matrix = {}
            for i in list(matrix_data.keys()):
                if i != "labels":
                    name = i.split("_")
                    name[1] = name[1].capitalize()
                    name = "".join(name)
                    renamed_recultivation_matrix[name] = matrix_data[i]
                else:
                    renamed_recultivation_matrix[i] = matrix_data[i]
            return renamed_recultivation_matrix

        base_zones_source = await urban_api_handler.get(
            extra_url=f"/api/v1/scenarios/{base_scenario_id}/functional_zone_sources",
            headers=self.headers,
        )
        target_zones_source = await urban_api_handler.get(
            extra_url=f"/api/v1/scenarios/{target_scenario_id}/functional_zone_sources",
            headers=self.headers,
        )
        base_source_params = await _form_source_params(base_zones_source)
        target_source_params = await _form_source_params(target_zones_source)
        base_func_zones = await urban_api_handler.get(
            extra_url=f"/api/v1/scenarios/{base_scenario_id}/functional_zones",
            headers=self.headers,
            params=base_source_params,
        )
        func_zones = await urban_api_handler.get(
            extra_url="/api/v1/scenarios/128/functional_zones",
            headers=self.headers,
            params=target_source_params,
        )
        base_ids = set([i["properties"]["functional_zone_type"]["id"] for i in base_func_zones["features"]])
        target_ids = set([i["properties"]["functional_zone_type"]["id"] for i in func_zones["features"]])
        matrix_labels = [str(i) for i in (base_ids | target_ids)]
        cost_matrix = await urban_api_handler.get(
            extra_url=f"/api/v1/profiles_reclamation/matrix?labels={','.join(matrix_labels)}&territory_id={territory_id}",
        )
        recultivation_matrix = await _map_matrix_names(cost_matrix)

        request_json = {
            "area": {
                "geometry": area,
                "sourcePzzAreas": [
                    {
                        "allowedCode": str(
                            i["properties"]["functional_zone_type"]["id"]
                        ),
                        "geometry": i["geometry"]
                    } for i in base_func_zones["features"]
                ],
                "targetPzzAreas": [
                    {
                        "allowedCode": str(
                            i["properties"]["functional_zone_type"]["id"]
                        ),
                        "geometry": i["geometry"]
                    } for i in func_zones["features"]
                ],
                "recultivationTable": recultivation_matrix,
            },
            "request": {
                "recultivation": True,
                "demolition": False,
                "construction": False,
                "allowExplosiveDemolition": False,
                "utilizationIndex": {
                    "costOfWork": 1.2,
                    "timeOfWork": 1.2
                },
                "breakdownsIndex": {
                    "costOfWork": 1.2,
                    "timeOfWork": 1.2
                },
                "hazardIndex": {
                    "costOfWork": 1.2,
                    "timeOfWork": 1.1
                }
            },
            "parameters": {
                "wasteEliminationAfterDismantlement": {
                    "costOfWork": 390.0,
                    "timeOfWork": 0.0001
                },
                "levelingAfterDismantlement": {
                    "costOfWork": 300.0,
                    "timeOfWork": 0.003
                },
                "footingDismantlementPerUnit": {
                    "costOfWork": 1500.0,
                    "timeOfWork": 0.01
                },
                "roofDismantlementPerUnit": {
                    "costOfWork": 500.0,
                    "timeOfWork": 0.015
                },
                "utilityDismantlementPerUnit": {
                    "costOfWork": 300.0,
                    "timeOfWork": 0.0005
                },
                "constructionSitePerUnit": {
                    "costOfWork": 200.0,
                    "timeOfWork": 0.005
                },
                "minExplosiveDistance": 100.0,
                "minMechanicalDistance": 100.0,
                "minMechanicalHeight": 20.0,
                "explosiveDemolition": {
                    "overlappingDemolition": {
                        "costOfWork": 100.0,
                        "timeOfWork": 0.0001
                    },
                    "wallsDemolition": {
                        "costOfWork": 100.0,
                        "timeOfWork": 0.0001
                    }
                },
                "mechanicalDemolition": {
                    "overlappingDemolition": {
                        "costOfWork": 600.0,
                        "timeOfWork": 0.004
                    },
                    "wallsDemolition": {
                        "costOfWork": 600.0,
                        "timeOfWork": 0.004
                    }
                },
                "halfMechanicalDemolition": {
                    "overlappingDemolition": {
                        "costOfWork": 3000.0,
                        "timeOfWork": 0.02
                    },
                    "wallsDemolition": {
                        "costOfWork": 3000.0,
                        "timeOfWork": 0.025
                    }
                },
                "depthIndex": 1.0
            }
        }

        response = await recultivation_api_handler.post(
            extra_url=f"/api/v1/redevelopment/calculate",
            data=request_json,
        )
        return response


indicators_savior_api_service = IndicatorsSaviorApiService()
