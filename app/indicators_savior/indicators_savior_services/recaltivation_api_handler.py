from app.common.api_handler.api_handler import AsyncApiHandler
from app.common.exceptions.http_exception_wrapper import http_exception
from app.common.config.config import config


class RecultivationApiHandler(AsyncApiHandler):
    """
    Class handles errors with requests to redevelopment generator
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

        super().__init__(base_url)

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

        response = await super().post(extra_url, data=data, params=params, headers=headers)
        if response["code"] != 0:
            if response["code"] == 1:
                raise http_exception(
                    500,
                    msg=f"Couldn't calculate time and money expenses from {self.base_url + extra_url}",
                    _input=data,
                    _detail=response["description"]
                )
            else:
                raise http_exception(
                    status_code=400,
                    msg=f"Couldn't extract time and money expenses query to {self.base_url + extra_url}",
                    _input=data,
                    _detail=response["description"]
                )
        else:
            return response


recultivation_api_handler = RecultivationApiHandler(config.get("REDEVELOPMENT_API_URL"))
