import json

from loguru import logger

from app.common import urban_api_handler
from app.common.api_handler.api_handler import (
    transport_frame_api_handler,
    townsnet_api_handler,
    eco_frame_api_handler,
    pop_frame_api_handler
)


class GeneratorApiService:
    """Class for retrieving data from urban api for grid generation"""

    def __init__(self):
        """
        Initialization function
        """

        self.territory = "/api/v1/territory"
        self.physical = "/api/v1/physical_objects"
        self.urban_extractor = urban_api_handler
        self.townsnet_extractor = townsnet_api_handler
        self.transport_frame_extractor = transport_frame_api_handler
        self.pop_frame_extractor = pop_frame_api_handler
        self.eco_frame_extractor = eco_frame_api_handler

    async def get_territory_data(
            self, territory_id: int
    ) -> dict | list:
        """
        Function retrieves territory data

        Args:
            territory_id (int): Territory ID

        Returns:
            dict: Territory data
        """

        response = await self.urban_extractor.get(
            extra_url=f"{self.territory}/{territory_id}",
            params={}
        )
        return response

    async def get_intersecting_geometry(
            self,
            territory_geometry: dict,
            physical_object_id: int
    ) -> dict | list:
        """
        Function retrieves intersecting physical objects geometries with provided territory geometry

        Args:
            territory_geometry (dict): Territory geometry
            physical_object_id (int): Physical object ID

        Return:
            dict | list: Intersecting physical objects geometries
        """

        url = f"{self.physical}/around"
        response = await self.urban_extractor.post(
            extra_url=url,
            params={
                "physical_object_type_id": physical_object_id
            },
            data=territory_geometry
        )
        return response

    async def get_social_provision_evaluation(
            self,
            territory_id: int,
            json_data: dict | list
    ):
        """
        Function retrieves evaluation for social provision
        Args:
            territory_id (int): Territory ID
            json_data (dict): Data for evaluation

        Returns:
            dict | list: Evaluated data
        """

        logger.info(f"Started provision extraction for {len(json_data['features'])} territories")
        response = await self.townsnet_extractor.post(
            extra_url=f"/provision/{territory_id}/get_evaluation",
            data=json_data
        )
        finished = False
        return response

    async def get_engineering_evaluation(
            self,
            territory_id: int,
            json_data: dict | list
    ) -> dict | list:
        """
        Function retrieves evaluation for engineering
        Args:
            territory_id (int): Territory ID
            json_data (dict): Data for evaluation

        Returns:
            dict | list: Evaluated data
        """

        response = await self.townsnet_extractor.post(
            extra_url=f"/engineering/{territory_id}/evaluate_geojson",
            data=json_data
        )
        return response

    async def get_transport_evaluation(
            self,
            territory_id: int
    ) -> dict | list:
        """
        Function retrieves transport frame
        Args:
            territory_id (int): Territory ID

        Returns:
            dict | list: Transport frame
        """

        response = await self.transport_frame_extractor.get(
            extra_url=f"/{territory_id}/transport_criteria"
        )
        return response

    async def get_ecological_evaluation(
            self,
            territory_id: int,
            json_data: dict | list
    ) -> dict | list:
        """
        Function retrieves evaluation for ecological
        Args:
            territory_id (int): Territory ID
            json_data (dict): Data for evaluation

        Returns:
            dict | list: Evaluated data
        """

        response = await self.eco_frame_extractor.post(
            extra_url=f"/ecoframe/eco_mark",
            params={
                "region_id": territory_id,
            },
            data=json_data
        )
        return response

    async def get_population_evaluation(
            self,
            territory_id: int,
            json_data: dict | list
    ) -> dict | list:
        """
        Function retrieves evaluation for population
        Args:
            territory_id (int): Territory ID
            json_data (dict): Data for evaluation

        Returns:
            dict | list: Evaluated data
        """

        response = await self.pop_frame_extractor.post(
            extra_url=f"/population/{territory_id}/evaluate",
            headers=townsnet_api_handler.bearer_token,
            data=json_data
        )
        return response

    async def get_hexes_from_db(
            self,
            territory_id: int
    ) -> dict | list:
        """
        Function retrieves hexes from db

        Returns:
            dict | list: Hexes
        """

        response = await self.urban_extractor.get(
            extra_url=f"{self.territory}/{territory_id}/hexagons",
            params={
                "centers_only": "true"
            }
        )
        return response

    async def post_hexes_to_db(
            self,
            territory_id: int,
            json_data: dict | list
    ) -> None:
        """
        Function posts hexes to db
        """

        await self.urban_extractor.post(
            extra_url=f"{self.territory}/{territory_id}/hexagons",
            data=json_data
        )

    async def delete_old_hexes_from_db(
            self,
            territory_id: int
    ) -> None:

        await self.urban_extractor.delete(
            extra_url=f"{self.territory}/{territory_id}/hexagons"
        )


generator_api_service = GeneratorApiService()
