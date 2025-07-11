import asyncio
import json

import aiohttp
from loguru import logger

from app.common.config import config
from app.common.exceptions.http_exception_wrapper import http_exception


class AsyncApiHandler:
    """
    Class for handling async requests to apies
    """

    def __init__(
            self,
            base_url: str,
    ) -> None:
        """
        Initialisation function

        Args:
            base_url (str): Base api url
            auth_header str: Bearer access token

        Returns:
            None
        """

        self.base_url = base_url

    async def get(
            self,
            extra_url: str,
            params: dict = None,
            headers: dict = None,
    ) -> dict:
        """
        Function extracts get query within extra url

        Args:
            extra_url (str): Endpoint url
            params (dict): Query parameters
            headers (dict): Headers for queries

        Returns:
            dict: Query result in dict format
        """

        endpoint_url = self.base_url + extra_url
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=endpoint_url,
                params=params,
                headers=headers,
            ) as response:
                if response.status == 200:
                    return await response.json()
                additional_info = await response.json()
                e = http_exception(
                    response.status,
                    "Error during extracting query",
                    _input={"url": endpoint_url, "params": params},
                    _detail=additional_info
                )
                logger.exception(e)
                raise e

    async def post(
            self,
            extra_url: str,
            data: dict | list,
            params: dict = None,
            headers: dict = None,
    ) -> dict:
        """
        Function extracts post query within extra url

        Args:
            extra_url (str): Endpoint url
            data (dict): Data to post | list
            params (dict): Query parameters. Default to None
            headers (dict): HTTP headers. Default to None

        Returns:
            dict: Query result in dict format | list
        """

        endpoint_url = self.base_url + extra_url
        async with aiohttp.ClientSession() as session:

            async with session.post(
                url=endpoint_url,
                headers=headers,
                params=params,
                json=data,
                timeout=int(config.get("GENERAL_TIMEOUT"))
            ) as response:
                if response.status in (200, 201):
                    # logger.info(
                    #     f"Posted data with url: {response.url} and status: {response.status}"
                    # )
                    await asyncio.sleep(0.1)
                    return await response.json()
                logger.warning(
                    f"""
                    Couldn't extract post request with url: {endpoint_url}, status code {response.status}
                    request_params: {params}
                    data: {data}
                    """
                )
                additional_info = await response.text()
                e = http_exception(
                    response.status,
                    "Error during extracting query",
                    _input={"url": endpoint_url, "params": params},
                    _detail=additional_info
                )
                with open(f'{"_".join(extra_url.split("/"))}_{response.status}_error', "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "error_info": additional_info,
                            "body": data,
                        },
                        f
                    )
                logger.exception(e)
                raise e

    async def put(
            self,
            extra_url: str,
            data: dict | list,
            session: aiohttp.ClientSession = None,
            params: dict = None,
            headers: dict = None,
    ) -> dict:
        """
        Function extracts put query within extra url

        Args:
            session (aiohttp.ClientSession): Session to extract requests
            extra_url (str): Endpoint url
            data (dict): Data to post | list
            params (dict): Query parameters. Default to None
            headers (dict): HTTP headers. Default to None

        Returns:
            dict: Query result in dict format | list
        """

        if not session:
            session = aiohttp.ClientSession()
        endpoint_url = self.base_url + extra_url
        async with session as session:
            async with session.put(
                url=endpoint_url,
                headers=headers,
                params=params,
                json=data,
                timeout=int(config.get("GENERAL_TIMEOUT"))
            ) as response:
                if response.status in (200, 201):
                    return await response.json()
                additional_info = await response.text()
                e = http_exception(
                    response.status,
                    "Error during extracting query",
                    _input={"url": endpoint_url, "params": params},
                    _detail=additional_info
                )
                logger.exception(e)
                raise e

    async def delete(
            self,
            extra_url: str,
            params: dict = None,
            headers: dict = None,
    ) -> None:
        """
        Function extracts delete query within extra url

        Args:
            extra_url (str): Endpoint url
            params (dict): Query parameters. Default to None
            headers (dict): HTTP headers. Default to None

        Returns:
            None
        """

        endpoint_url = self.base_url + extra_url
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=endpoint_url,
                params=params,
                headers=headers,
            ) as response:
                if response.status in (200, 201):
                    logger.info(
                        f"Delete data with url: {response.url} and status: {response.status}")
                    return await response.json()

                additional_info = await response.text()
                e = http_exception(
                    response.status,
                    "Error during extracting query",
                    _input={"url": endpoint_url, "params": params},
                    _detail=additional_info
                )
                logger.exception(e)
                raise e

    # async def townsnet_post(
    #         self,
    #         extra_url: str,
    #         data: dict | list,
    #         params: dict = None,
    #         headers: dict = None,
    # ) -> dict:
    #     """
    #     Function extracts post query within extra url
    #
    #     Args:
    #         extra_url (str): Endpoint url
    #         data (dict): Data to post | list
    #         params (dict): Query parameters. Default to None
    #         headers (dict): HTTP headers. Default to None
    #
    #     Returns:
    #         dict: Query result in dict format | list
    #     """
    #
    #     endpoint_url = self.base_url + extra_url
    #
    #     try:
    #         result = await self.post(
    #             extra_url=extra_url,
    #             data=data,
    #             params=params,
    #             headers=headers,
    #             )
    #         return result
    #     except HTTPException as e:
    #         if e.status == 404 and e._detail["detail"].split(" ")[0] == "Most"
    #             await self.post(
    #                 extra_url=""
    #             )
    #
    #
    #             else:
    #                 additional_info = await response.json()
    #             logger.warning(
    #                 f"""
    #                                 Couldn't extract post request with url: {endpoint_url}, status code {response.status}
    #                                 request_params: {params}
    #                                 data: {data}
    #                                 """
    #             )
    #             raise http_exception(
    #                 response.status,
    #                 "Error during extracting query",
    #                 _input={"url": endpoint_url, "params": params},
    #                 _detail=additional_info
    #             )


urban_api_handler = AsyncApiHandler(config.get("URBAN_API"))
townsnet_api_handler = AsyncApiHandler(config.get("TOWNSNET_API"))
transport_frame_api_handler = AsyncApiHandler(config.get("TRANSPORT_FRAME_API"))
pop_frame_api_handler = AsyncApiHandler(config.get("POP_FRAME_API"))
eco_frame_api_handler = AsyncApiHandler(config.get("ECOFRAME_API"))
landuse_det_api_handler = AsyncApiHandler(config.get("LANDUSE_DET_API"))
