import geopandas as gpd

from .generator_api_service import generator_api_service
from .grid_generator import grid_generator


class GridGeneratorService:

    @staticmethod
    async def generate_grid(
            territory_id
    ) -> dict:
        """
        Function generates hexagonal grid for provided territory.

        Args:
            territory_id (int): The territory to be generated on.

        Returns:
            dict: The generated hexagonal grid.
        """

        territory_data = await generator_api_service.gry_territory_data(territory_id)
        territory = territory_data.get("data")
        grid = await grid_generator.generate_hexagonal_grid(territory)
        return grid
