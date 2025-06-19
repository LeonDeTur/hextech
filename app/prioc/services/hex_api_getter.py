import asyncio

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

from app.common import config, urban_api_handler

bucket_name = config.get("FILESERVER_BUCKET_NAME")
lo_hexes_filename= config.get("FILESERVER_LO_NAME")

indicators_names = ['Население',
 'Транспортное обеспечение',
 'Экологическая ситуация',
 'Социальное обеспечение',
 'Обеспечение инженерной инфраструктурой']
hexes_attributes_list = indicators_names + ["geometry"]


class HexApiService:
    """Class for retrieving hexagons necessary data for priority objects calculations"""

    def __init__(
            self,
            territory_url="/api/v1/territory",
            scenarios_url="/api/v1/scenarios",
            physical="/api/v1/physical_objects/around",
    ):
        """
        Initialization function

        Args:
            territory_url (string): Base URL for requests

        Returns:
            None
        """

        self.territory_url = territory_url
        self.extractor = urban_api_handler
        self.scenarios_url = scenarios_url
        self.physical = physical

    # ToDo make more flexible
    async  def get_hexes_with_indicators_by_territory(
            self,
            regional_scenario_id: int
    ) -> gpd.GeoDataFrame:
        """
        Function retrieves hexagons layer with indicators
        Args:
            regional_scenario_id (int): Regional scenario ID
        Returns:
            gpd.GeoDataFrame: Hexagons with indicators values as layers attributes in 4326 crs
        """

        url = f"{self.scenarios_url}/{regional_scenario_id}/indicators_values/hexagons"
        response = await self.extractor.get(
            extra_url=url,
        )
        gdf = gpd.GeoDataFrame.from_features(response, crs=4326)
        df_records = await asyncio.to_thread(
            gdf["indicators"].apply,
            func=lambda x: {i["name_full"] : i["value"] if i else None for i in x},
        )
        indicators_df = pd.DataFrame.from_records(df_records)
        keep_columns = ["geometry", "hexagon_id"] + indicators_names
        result = pd.concat([gdf, indicators_df], axis=1)
        result = result[keep_columns]
        result.dropna(inplace=True)
        return result

    async def get_positive_service_by_territory_id(
            self,
            territory_geometry: dict,
            physical_object_ids=None
    ) -> gpd.GeoDataFrame | pd.DataFrame:
        """
        Function retrieves intersecting physical objects geometries with provided territory geometry

        Args:
            territory_geometry (dict): Territory geometry
            physical_object_ids (list[int]): Physical object IDs list. Default to water objects

        Return:
            gpd.GeoDataFrame | pd.DataFrame: Intersecting physical objects geometries to clean
        """

        if physical_object_ids is None:
            physical_object_ids = [45, 55]
        physical_obj = []
        for phys_id in physical_object_ids:
            url = f"{self.physical}?physical_object_type_id={phys_id}"
            response = await self.extractor.post(
                extra_url=url,
                data=territory_geometry
            )
            tmp_gdf = gpd.GeoDataFrame(geometry=[shape(i["geometry"]) for i in response], crs=4326)
            physical_obj.append(tmp_gdf)

        result_gdf = pd.concat(physical_obj)

        if isinstance(result_gdf, gpd.GeoDataFrame):
            if not result_gdf.empty:
                result_gdf.set_crs(4326, inplace=True)
            return result_gdf
        result_gdf = gpd.GeoDataFrame()
        return result_gdf

    async def get_negative_service_by_territory_id(
            self,
            territory_id: int,
            service_type_ids: list[int],
    ) -> gpd.GeoDataFrame | pd.DataFrame:
        """
        Function retrieves negative services layer
        Args:
            territory_id (integer): Territory ID
            service_type_ids (list[int]): Service type ids for retrieving
        Returns:
            gpd.GeoDataFrame: Services centroids with indicators values as layers attributes
        """

        url = f"{self.territory_url}/{territory_id}/services_geojson"
        result_gdf = gpd.GeoDataFrame()
        for service_type_id in service_type_ids:
            current_url = url
            response = await self.extractor.get(
                extra_url=current_url,
                params={
                    "service_type_id": service_type_id,
                    "cities_only": "false",
                    "centers_only": "true"
                },
            )

            current_gdf = gpd.GeoDataFrame.from_features(response)
            result_gdf = pd.concat([result_gdf, current_gdf])

        if isinstance(result_gdf, gpd.GeoDataFrame):
            if not result_gdf.empty:
                result_gdf.set_crs(4326, inplace=True)
            return result_gdf
        result_gdf = gpd.GeoDataFrame()
        return result_gdf

    @staticmethod
    async def get_regional_base_scenario(territory_id: int) -> int:
        """
        Function retrieves regional base scenario by territory id
        Args:
            territory_id (int): Territory ID
        Returns:
            int: Base scenario
        """

        response = await urban_api_handler.get(
            extra_url="/api/v1/scenarios",
            params={
                "territory_id": territory_id,
                "is_based": "true"
            }
        )
        return response[0]["scenario_id"]


hex_api_getter = HexApiService()
