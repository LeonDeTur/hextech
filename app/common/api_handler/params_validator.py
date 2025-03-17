from .api_handler import urban_api_handler

class ParamsValidator:
    """
    Class for getting limitations from urban_api
    """

    def __init__(self):
        self.urban_extractor = urban_api_handler

    async def extract_current_regions(
            self,
            ids_only: bool = True,
    ) -> list[dict[str, int]] | list[int]:
        """
        Functions extracts regions available in db

        Args:
            ids_only (bool, optional): return_only_ids

        Returns:
            list[dict[str, int]]: list of dictionaries available regions ids with names
        """

        result = await self.urban_extractor.get(
            extra_url="/api/v1/all_territories_without_geometry",
            params={
                "parent_id": 12639,
            }
        )

        if ids_only:
            # result_list = [item["territory_id"] for item in result if item["territory_id"] == 1]
            result_list = [item["territory_id"] for item in result]
            return result_list
        # result_list = [
        #     {
        #         "id": item["territory_id"],
        #         "name": item["name"],
        #     }
        #     for item in result if item["territory_id"] == 1
        # ]
        result_list = [
            {
                "id": item["territory_id"],
                "name": item["name"],
            }
            for item in result
        ]
        return result_list


params_validator = ParamsValidator()
