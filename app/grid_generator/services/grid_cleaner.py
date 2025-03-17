import geopandas as gpd


class GridCleaner:
    """
    Class for cleaning grid from objects
    """

    @staticmethod
    async def clean__hex_grid_from(
            hex_grid: gpd.GeoDataFrame,
            objects: gpd.GeoDataFrame
    ) -> gpd.GeoDataFrame:
        """
        Function cleans hexagonal grid within objects geometries.

        Args:
            hex_grid (gpd.GeoDataFrame): Hexagonal grid
            objects (gpd.GeoDataFrame): Objects to clean from

        Returns:
            gpd.GeoDataFrame: Cleaned hexagonal grid
        """

        drop_indexes = hex_grid.sjoin(objects, predicate='within').index.to_list()
        cleaned_grid = hex_grid.drop(drop_indexes)
        return cleaned_grid


grid_cleaner = GridCleaner()
