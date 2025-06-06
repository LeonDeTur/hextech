import json
import asyncio

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape
from loguru import logger

from .generator_api_service import generator_api_service
from .grid_generator import grid_generator
from .potential_estimator import potential_estimator
from .constants.constants import prioc_objects_types
from app.common import http_exception, params_validator, tasks_api_handler
from app.prioc.services.prioc_service import prioc_service


class GridGeneratorService:
    """
    Class for grid generation service logic
    """

    @staticmethod
    async def get_cleaning_gdf(
            territory_id: int,
            objects_ids: list[int]
    ) -> gpd.GeoDataFrame | pd.DataFrame:
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
        objects_cleaning_cors = [generator_api_service.get_intersecting_geometry(
                territory_data["geometry"],
            obj_id
            ) for obj_id in objects_ids]
        results = await asyncio.gather(*objects_cleaning_cors)
        for result in results:
            geometries = [shape(item["geometry"]) for item in result]
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
            pure: bool = False
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
        if territory_id in [3268, 3138, 16141]:
            grid = await grid_generator.generate_hexagonal_grid(territory, size=8)
        else:
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

        if territory_id not in await params_validator.extract_current_regions():
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

        results = await tasks_api_handler.extract_requests_to_several_urls(
            api_queries=functions_to_extract,
            territory_id=territory_id,
            geojson_data=feature_collection_grid,
        )
        grid.drop_duplicates("geometry", inplace=True)
        for result in results:
            key, item = zip(*result.items())
            try:
                if len(item) > len(grid):
                    item = item[:len(grid)]
                grid[key[0]] = item[0]
            except ValueError as e:
                logger.error(f"Error during indicators extraction: {str(e)}")
                raise http_exception(
                    status_code=500,
                    msg=f"Error during indicators extraction",
                    _input={"key": key, "item": item},
                    _detail={"Error": e.__str__()},
                )
        return grid

    async def generate_grid_with_indicators(
            self,
            territory_id: int,
    ) -> gpd.GeoDataFrame | dict:
        """
        Function generates hexagonal grid for provided territory and saves it to db.

        Args:
            territory_id (int): The territory to be generated on.

        Returns:
            dict: The generated hexagonal grid in geojson format or dict with additional information.
        """

        if territory_id not in await params_validator.extract_current_regions():
            raise http_exception(
                400,
                msg="No territories supported accept LO with id=1",
                _input=f"{territory_id}",
                _detail="Just wait while 507 will start refactoring or their api dies finally..."
            )

        grid = await self.generate_grid(territory_id)
        grid_with_indicators = await self.calculate_grid_indicators(grid, territory_id)
        grid_with_profiles = await potential_estimator.estimate_potentials(grid_with_indicators)
        return grid_with_profiles

    async def bound_hexagons_indicators(
            self,
            territory_id: int
    ) -> dict:
        """
        Function wrights hexagons indicators to db
        """

        regional_scenario = await generator_api_service.get_regional_base_scenario(territory_id)
        hexagons_geojson = await generator_api_service.get_hexes_from_db(territory_id)
        grid = gpd.GeoDataFrame.from_features(hexagons_geojson, crs=4326)
        grid_with_indicators = await self.calculate_grid_indicators(grid, territory_id)
        bounded_hexagons = await potential_estimator.estimate_potentials(grid_with_indicators)
        for i in prioc_objects_types:
            current_object_hexes = await prioc_service.get_hexes_for_object_from_gdf(
                hexes=bounded_hexagons,
                territory_id=territory_id,
                object_type=i
            )
            bounded_hexagons = pd.merge(
                bounded_hexagons,
                current_object_hexes[["hexagon_id", "weighted_sum"]],
                on="hexagon_id", how="outer"
            )
            if i == "Пром объект":
                bounded_hexagons.rename(columns={"weighted_sum": "Промышленная зона"}, inplace=True)
            elif i == "Логистическо-складской комплекс":
                bounded_hexagons.rename(columns={"weighted_sum": "Логистический, складской комплекс"}, inplace=True)
            elif i == "Кампус университетский":
                bounded_hexagons.rename(columns={"weighted_sum": "Университетский кампус"}, inplace=True)
            elif i == "Тур база":
                bounded_hexagons.rename(columns={"weighted_sum": "Туристическая база"}, inplace=True)
            else:
                bounded_hexagons.rename(columns={"weighted_sum": i}, inplace=True)
        full_map = await generator_api_service.extract_all_indicators()
        mapped_name_id = {}
        for item in full_map:
            if item["name_full"] in bounded_hexagons.columns:
                mapped_name_id[item["name_full"]] = item["indicator_id"]
            elif item["name_short"] in bounded_hexagons.columns:
                mapped_name_id[item["name_short"]] = item["indicator_id"]
        bounded_hexagons.drop_duplicates("geometry", inplace=True)
        df_to_put = bounded_hexagons.drop(columns=["geometry", "properties"])
        columns_to_iter = list(df_to_put.drop(columns="hexagon_id").columns)
        extract_list = []
        failed_list = []
        for index, row in df_to_put.iterrows():
            for column in columns_to_iter:
                if not pd.isna(row[column]):
                    extract_list.append(
                        {
                        "indicator_id": int(mapped_name_id[column]),
                        "scenario_id": regional_scenario,
                        "territory_id": None,
                        "hexagon_id": int(row["hexagon_id"]),
                        "value": row[column],
                        "comment": "--",
                        "information_source": "hextech/grid_generator",
                        "properties": {}
                        }
                    )
                elif int(mapped_name_id[column]) in [197, 198, 199, 200, 201]:
                    failed_object = {
                        "indicator_id": int(mapped_name_id[column]),
                        "scenario_id": regional_scenario,
                        "territory_id": None,
                        "hexagon_id": int(row["hexagon_id"]),
                        "value": None,
                        "comment": "--",
                        "information_source": "hextech/grid_generator",
                        "properties": {}
                        }
                    failed_list.append(failed_object)
                else:
                    failed_object = {
                        "indicator_id": int(mapped_name_id[column]),
                        "scenario_id": regional_scenario,
                        "territory_id": None,
                        "hexagon_id": int(row["hexagon_id"]),
                        "value": None,
                        "comment": "--",
                        "information_source": "hextech/grid_generator",
                        "properties": {}
                        }
                    failed_list.append(failed_object)

        with open(f"failed_grid_indicators_list.json", "w") as f:
            json.dump(failed_list, f)
        await generator_api_service.put_hexagon_data(extract_list, regional_scenario)

        return {"msg": f"Successfully uploaded hexagons data for {territory_id}"}


grid_generator_service = GridGeneratorService()
