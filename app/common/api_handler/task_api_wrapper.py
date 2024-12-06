import asyncio

from app.common.config import config


class TasksApiHandler:
    """
    Class for wrapping api requests to threads.
    """

    @staticmethod
    async def extract_requests_to_several_urls(
            api_queries: list,
            territory_id: int,
            geojson_data: dict
    ) -> list:
        """
        Function executes api map in threads

        Args:
            api_queries: list of api queries functions
            territory_id: territory id
            geojson_data: geojson data

        Returns:
            list of api queries functions results
        """

        tasks = [extraction(territory_id, geojson_data) for extraction in api_queries]
        result = await asyncio.gather(*tasks)
        return result

    @staticmethod
    async def extract_requests_to_one_url(
            api_query,
            params: list
    ) -> list:
        """
        Function executes few api queries to one endpoint

        Args:
            api_query: api query
            params: list of parameters

        Returns:
            list of api queries results
        """

        tasks = [api_query(param) for param in params]
        result = await asyncio.gather(*tasks)
        return result




tasks_api_handler = TasksApiHandler()
