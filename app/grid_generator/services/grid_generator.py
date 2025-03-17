import geopandas as gpd
import h3
from shapely.geometry import shape


class GridGenerator:

    @staticmethod
    async def generate_hexagonal_grid(
            territory: gpd.GeoDataFrame,
            size: int = 6,
    ) -> gpd.GeoDataFrame:
        """
        Function generates hexagonal grid for provided territory.

        Args:
            territory (gpd.GeoDataFrame): The territory to be generated on.
            size (int, optional): Size of hexagonal grid. Defaults to 6.

        Returns:
            gpd.GeoDataFrame: The generated hexagonal grid.
        """

        if territory.crs != 4326:
            territory.to_crs(4326, inplace=True)
        cells = h3.geo_to_cells(territory.union_all(), res=size)
        geometries = [shape(h3.cells_to_geo([cell])) for cell in cells]
        result = gpd.GeoDataFrame(geometry=geometries, crs=territory.crs)
        return result

grid_generator = GridGenerator()
