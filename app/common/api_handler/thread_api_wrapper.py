import asyncio
from concurrent.futures import ThreadPoolExecutor

import geopandas as gpd

from .api_handler import AsyncApiHandler
from app.common.config import config


class ThreadApiHandler:
    """
    Class for wrapping api requests to threads.
    """

    def __init__(self, workers):
        self.workers = workers

    async def extract_multiple_requests_in_treads(
            self,
            api_queries: list,
            territory_id: int,
            geojson_data: dict
    ) -> list:
        """
        Function executes api map in threads
        """

        def async_wrapper(coro):
            return asyncio.run(coro)

        def execute_threads(workers: int):
            with ThreadPoolExecutor(max_workers=workers) as executor:
                coros = [item(territory_id, geojson_data) for item in api_queries]
                responses = []
                for func_res in executor.map(async_wrapper, coros):
                    responses.append(func_res)
                return responses

        response = execute_threads(self.workers)
        return response

    # async def extract_request_in_thread(
    # self,
    # workers: int
    # ):




thread_api_handler = ThreadApiHandler(int(config.get("MAX_WORKERS")))
