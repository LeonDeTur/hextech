import json

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape
from loguru import logger

from .generator_api_service import generator_api_service
from .grid_generator import grid_generator
from .potential_estimator import potential_estimator
from app.common import http_exception, params_validator, thread_api_handler


class GridGeneratorService:
    """
    Class for grid generation service logic
    """

    @staticmethod
    async def get_cleaning_gdf(
            territory_id: int,
            objects_ids: list[int]
    ) -> gpd.GeoDataFrame:
        """
        Function retrieves geometries to clean hexagons

        Args:
            territory_id (int): Territory ID
            objects_ids (list[int]): Objects IDs

        Returns:
            gpd.GeoDataFrame: Geometries to clean hexagons
        """

        physical_obj = []
        territory_data = await generator_api_service.get_territory_data(territory_id)

        for obj_id in objects_ids:
            current_obj_collection_list = await generator_api_service.get_intersecting_geometry(
                territory_data["geometry"],
                obj_id
            )
            geometries = [shape(item["geometry"]) for item in current_obj_collection_list]
            physical_obj.append(gpd.GeoDataFrame(geometry=geometries, crs=4326))

        result = pd.concat(physical_obj)
        return result

    @staticmethod
    async def save_new_hexagons(
            territory_id: int,
            feature_collection_hexes: dict
    ) -> dict[str, str]:
        """
        Function deletes old hexes from db in exists

        Args:
            territory_id (int): Territory ID
            feature_collection_hexes (dict): Hexes to post

        Returns:
            dict: with save info
        """
        existing_hexes = await generator_api_service.get_hexes_from_db(territory_id)
        if existing_hexes["features"]:
            await generator_api_service.delete_old_hexes_from_db(territory_id)
        hexes_to_write = [hexagon for hexagon in feature_collection_hexes["features"]]
        await generator_api_service.post_hexes_to_db(
            territory_id=territory_id,
            json_data=hexes_to_write
        )
        msg = """Successfully generated hexagonal grid and saved to db.
            Check result with get method in urban_api (territory/{territory_id}/hexagons)"""
        return {
            "msg": msg,
        }

    async def generate_grid(
            self,
            territory_id,
            pure: bool = True
    ) -> gpd.GeoDataFrame:
        """
        Function generates hexagonal grid for provided territory.

        Args:
            territory_id (int): The territory to be generated on.
            pure (bool, optional): If True, grid will be cleaned from objects. Defaults to True.

        Returns:
            dict: The generated hexagonal grid.
        """

        available_ids = await params_validator.extract_current_regions()
        if territory_id not in available_ids:
            raise http_exception(
                400,
                msg="Territory ID is not implemented",
                _input=territory_id,
                _detail=f"List of available territories {available_ids}"
            )

        logger.info(f"Starting geometry retrieving for territory with id {territory_id}")
        territory_data = await generator_api_service.get_territory_data(territory_id)
        territory = gpd.GeoDataFrame(geometry=[shape(territory_data["geometry"])], crs=4326)
        logger.info(f"Got geometry for territory with id {territory_id}, starting grid generation")
        grid = await grid_generator.generate_hexagonal_grid(territory)
        logger.info(f"Finished grid generation{territory_id}, starting grid clarification")
        if pure:
            water = await self.get_cleaning_gdf(territory_id, [45, 55])
            drop_index = grid.sjoin(water, predicate='within').index.to_list()
            grid.drop(drop_index, inplace=True)
        return grid

    @staticmethod
    async def calculate_grid_indicators(
            grid: gpd.GeoDataFrame,
            territory_id: int,
    ) -> gpd.GeoDataFrame:
        """
        Function calculates indicators for grid

        Args:
            grid (gpd.GeoDataFrame): Hexagonal grid
            territory_id (int): Territory ID

        Returns:
            gpd.GeoDataFrame: Grid with indicators
        """

        if grid.crs  != 4326:
            grid.to_crs(4326, inplace=True)
        feature_collection_grid = json.loads(grid.to_json())

        #ToDo Rewrite when other regions will be available
        if territory_id != 1:
            raise http_exception(
                400,
                msg="Territory IDs except 1 are not implemented in connected apies",
                _input=territory_id,
                _detail="Ask 507 for further information"
            )

        functions_to_extract = [
            generator_api_service.get_social_provision_evaluation,
            generator_api_service.get_engineering_evaluation,
            generator_api_service.get_transport_evaluation,
            generator_api_service.get_ecological_evaluation,
            generator_api_service.get_population_evaluation
        ]

        results = await thread_api_handler.extract_multiple_requests_in_treads(
            api_queries=functions_to_extract,
            territory_id=territory_id,
            geojson_data=feature_collection_grid,
        )
        # logger.info(f"Starting indicators calculation for grid with territory id {territory_id}")
        # logger.info(f"Started social indicator evaluation for grid with territory id {territory_id}")
        # social = await generator_api_service.get_social_provision_evaluation(
        #     territory_id,
        #     feature_collection_grid
        # )
        # logger.info(f"Started engineering indicators calculation for grid with territory id {territory_id}")
        # engineering = await generator_api_service.get_engineering_evaluation(
        #     territory_id,
        #     feature_collection_grid
        # )
        # logger.info(f"Started transport indicators calculation for grid with territory id {territory_id}")
        # transport = await generator_api_service.get_transport_evaluation(
        #     territory_id,
        #     feature_collection_grid
        # )
        # logger.info(f"Started ecology indicators calculation for grid with territory id {territory_id}")
        # ecology = await generator_api_service.get_ecological_evaluation(
        #     territory_id,
        #     {"feature_collection": feature_collection_grid}
        # )
        # logger.info(f"Started population indicators calculation for grid with territory id {territory_id}")
        # population = await generator_api_service.get_population_evaluation(
        #     territory_id,
        #     feature_collection_grid
        # )
        # indicators_data = [
        #     social,
        #     engineering,
        #     transport,
        #     ecology,
        #     population
        # ]
        # columns = ['Показатель: Население',
        #            'Показатель: Транспорт',
        #            'Показатель: Экология',
        #            'Показатель: Социальная обеспеченность',
        #            'Показатель: Инженерная инфраструктура'
        #            ]
        #
        # grid[columns] = indicators_data

        results_df = pd.DataFrame.from_dict(results, orient='columns')
        grid_with_indicators = grid.merge(results_df, left_index=True, right_index=True)
        return grid_with_indicators

    async def generate_grid_with_indicators(
            self,
            territory_id: int,
            save_to_db: bool = False,
    ) -> dict:
        """
        Function generates hexagonal grid for provided territory and saves it to db.

        Args:
            territory_id (int): The territory to be generated on.
            save_to_db (bool, optional): If True, grid will be saved to db.

        Returns:
            dict: The generated hexagonal grid in geojson format or dict with additional information.
        """

        if territory_id != 1:
            raise http_exception(
                400,
                msg="No territories supported accept LO with id=1",
                _input=f"{territory_id}",
                _detail="Just wait while 507 will start refactoring or their api dies finally..."
            )

        grid = await self.generate_grid(territory_id)
        grid_with_indicators = await self.calculate_grid_indicators(grid, territory_id)
        grid_with_profiles = await potential_estimator.estimate_potentials(grid_with_indicators)
        geojson_grid = json.loads(grid_with_profiles.to_json())
        if save_to_db:
            result = await self.save_new_hexagons(territory_id, geojson_grid)
            return result

        return geojson_grid


grid_generator_service = GridGeneratorService()
