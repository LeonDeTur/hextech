import json

from pydantic import BaseModel, Field

from app.common.geometries import Geometry


with open("app/prioc/dto/example_territory.json", "r") as et:
    example_territory = json.load(et)


class TerritoryDTO(BaseModel):

    territory_id: int = Field(..., examples=[1], description="The id of the territory")
    territory: Geometry = Field(..., examples=[example_territory], description="The territory polygon")
