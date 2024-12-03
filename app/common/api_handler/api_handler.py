import aiohttp

from app.common.config import config
from app.common.exceptions.http_exception_wrapper import http_exception


class AsyncApiHandler:
    """
    Class for handling async requests to apies
    """

    def __init__(
            self,
            base_url: str
    ) -> None:
        """
        Initialisation function

        Args:
            base_url (str): Base api url

        Returns:
            None
        """

        self.base_url = base_url

    async def get(
            self,
            extra_url: str,
            params: dict
    ) -> dict:
        """
        Function extracts get query within extra url

        Args:
            extra_url (str): Endpoint url
            params (dict): Query parameters

        Returns:
            dict: Query result in dict format
        """

        endpoint_irl = self.base_url + extra_url
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=endpoint_irl,
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                additional_info = await response.json()
                raise http_exception(
                    response.status,
                    "Error during extracting query",
                    _input={
                        "url": endpoint_irl,
                        "params": params
                    },
                    _detail=additional_info
                )


urban_api_handler = AsyncApiHandler(config.get("URBAN_API"))
