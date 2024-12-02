import json

import geopandas as gpd
import pandas as pd

from .generator_api_service import generator_api_service
from .grid_generator import grid_generator


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
        for obj_id in objects_ids:
            current_feature_collection = await generator_api_service.get_physical_objects_to_clean(territory_id, obj_id)
            physical_obj.append(gpd.GeoDataFrame.from_features(current_feature_collection, crs=4326))

        result = pd.concat(physical_obj)
        return result

    @staticmethod
    async def save_new_hexagons(
            territory_id: int,
            feature_collection_hexes: dict
    ) -> None:
        """
        Function deletes old hexes from db in exists

        Args:
            territory_id (int): Territory ID
            feature_collection_hexes (dict): Hexes to post

        Returns:
            None
        """
        existing_hexes = await generator_api_service.get_hexes_from_db(territory_id)
        if existing_hexes["features"]:
            await generator_api_service.delete_old_hexes_from_db(territory_id)
        await generator_api_service.post_hexes_to_db(
            territory_id=territory_id,
            json_data=feature_collection_hexes
        )

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

        territory_data = await generator_api_service.get_territory_data(territory_id)
        territory = territory_data.get("data")
        grid = await grid_generator.generate_hexagonal_grid(territory)
        if pure:
            water = await self.get_cleaning_gdf(territory_id, [45, 55])
            drop_index = grid.sjoin(water, predicate='within').index.to_list()
            grid.drop(drop_index, inplace=True)
        return grid

    # ToDo Implement api calculations for indicators
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

        social = await generator_api_service.get_social_provision_evaluation(
            territory_id,
            feature_collection_grid
        )
        engineering = await generator_api_service.get_urban_engineering_evaluation(
            territory_id,
            feature_collection_grid
        )
        transport = await generator_api_service.get_transport_evaluation(
            territory_id,
            feature_collection_grid
        )
        ecology = await generator_api_service.get_ecology_evaluation(
            territory_id,
            feature_collection_grid
        )
        population = await generator_api_service.get_population_evaluation(
            territory_id,
            feature_collection_grid
        )
        indicators_data = [
            social,
            engineering,
            transport,
            ecology,
            population
        ]
        columns = ['Показатель: Население',
                   'Показатель: Транспорт',
                   'Показатель: Экология',
                   'Показатель: Социальная обеспеченность',
                   'Показатель: Инженерная инфраструктура'
                   ]

        grid[columns] = indicators_data
        return grid

    async def generate_grid_with_indicators_to_db(
            self,
            territory_id: int,
    ) -> dict:
        """
        Function generates hexagonal grid for provided territory and saves it to db.

        Args:
            territory_id (int): The territory to be generated on.

        Returns:
            gpd.GeoDataFrame: The generated hexagonal grid.
        """

        grid = await self.generate_grid(territory_id)
        grid_with_indicators = await self.calculate_grid_indicators(grid, territory_id)
        geojson_grid = json.loads(grid_with_indicators.to_json())
        await self.save_new_hexagons(territory_id, geojson_grid)

        return geojson_grid


grid_generator_service = GridGeneratorService()
