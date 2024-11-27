from pydantic import BaseModel, Field
from pydantic_geojson import PolygonModel


class TerritoryDTO(BaseModel):

    territory_id: int = Field(..., description="The id of the territory")
    territory: PolygonModel

    @classmethod
    def as_form(
            cls,
            territory_id: int,
            territory: PolygonModel,
    ) -> "TerritoryDTO":
        return TerritoryDTO(
            territory_id=territory_id,
            territory=territory,
        )
