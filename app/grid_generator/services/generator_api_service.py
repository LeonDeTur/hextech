from app.common import urban_api_handler


class GeneratorApiService:
    """Class for retrieving data from urban api for grid generation"""

    def __init__(self):
        """
        Initialization function
        """

        self.territory = "/api/v1/territory"
        self.extractor = urban_api_handler

    async def gry_territory_data(
            self, territory_id: int
    ) -> dict | list:
        """
        Function retrieves territory data

        Args:
            territory_id (int): Territory ID

        Returns:
            dict: Territory data
        """

        response = await self.extractor.get(
            extra_url=f"{self.territory}/{territory_id}",
            params={}
        )
        return response

    async def get_objects_to_clean(
            self,
            territory_id: int
    ) -> dict | list:
        """
        Function retrieves objects to clean grid from

        Args:
            territory_id (int): Territory ID
        """

        response = await  self.extractor.get(

        )

generator_api_service = GeneratorApiService()
