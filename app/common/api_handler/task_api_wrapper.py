import asyncio

import aiohttp

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
            func,
            data: list[dict],
            headers: dict,
            max_concurrent_requests: int = 4
    ) -> list:
        """
        Function executes few api queries to one endpoint

        Args:
            func: function to execute
            data (list[dict]): data for api request
            headers: headers for api request
            max_concurrent_requests (int): maximum number of concurrent requests

        Returns:
            list of api queries results
        """

        semaphore = asyncio.Semaphore(max_concurrent_requests)

        async def bound_func(data_obj):
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    return await func(session=session, headers=headers, **data_obj)

        tasks_list = [bound_func(data_obj) for data_obj in data]
        result = await asyncio.gather(*tasks_list, return_exceptions=True)
        return result




tasks_api_handler = TasksApiHandler()
