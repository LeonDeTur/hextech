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
            auth_header: str = None
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
        if auth_header:
            self.auth_header = {"Authorization": auth_header}
        else:
            self.auth_header = None

    async def get(
            self,
            extra_url: str,
            params: dict = None
    ) -> dict:
        """
        Function extracts get query within extra url

        Args:
            extra_url (str): Endpoint url
            params (dict): Query parameters

        Returns:
            dict: Query result in dict format
        """

        endpoint_url = self.base_url + extra_url
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=endpoint_url,
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                additional_info = await response.json()
                raise http_exception(
                    response.status,
                    "Error during extracting query",
                    _input={
                        "url": endpoint_url,
                        "params": params
                    },
                    _detail=additional_info
                )

    async def post(
            self,
            extra_url: str,
            data: dict | list,
            params: dict = None
    ) -> dict:
        """
        Function extracts post query within extra url

        Args:
            extra_url (str): Endpoint url
            data (dict): Data to post | list
            params (dict): Query parameters. Default to None

        Returns:
            dict: Query result in dict format | list
        """

        endpoint_url = self.base_url + extra_url
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=endpoint_url,
                headers=self.auth_header,
                params=params,
                json=data,
                timeout=int(config.get("GENERAL_TIMEOUT"))
            ) as response:
                if response.status in (200, 201):
                    logger.info(
                        f"Posted data with url: {response.url} and status: {response.status}"
                    )
                    return await response.json()
                additional_info = await response.json()
                raise http_exception(
                    response.status,
                    "Error during extracting query",
                    _input={"url": endpoint_url, "params": params},
                    _detail=additional_info
                )

    async def delete(
            self,
            extra_url: str,
            params: dict = None
    ) -> None:
        """
        Function extracts delete query within extra url

        Args:
            extra_url (str): Endpoint url
            params (dict): Query parameters. Default to None

        Returns:
            None
        """

        endpoint_url = self.base_url + extra_url
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url=endpoint_url,
                params=params
            ) as response:
                if response.status not in (200, 204):
                    return await response.json()
                additional_info = await response.json()
                raise http_exception(
                    response.status,
                    "Error during extracting query",
                    _input={"url": endpoint_url, "params": params},
                    _detail=additional_info
                )


urban_api_handler = AsyncApiHandler(config.get("URBAN_API"))
townsnet_api_handler = AsyncApiHandler(config.get("TOWNSNET_API"))
transport_frame_api_handler = AsyncApiHandler(config.get("TRANSPORT_FRAME_API"))
pop_frame_api_handler = AsyncApiHandler(
    config.get("POP_FRAME_API"),
    "Bearer" + config.get("POP_FRAME_TOKEN")
)
eco_frame_api_handler = AsyncApiHandler(config.get("ECOFRAME_API"))
