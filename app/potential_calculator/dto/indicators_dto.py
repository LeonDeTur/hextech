# import json
#
# from pydantic import BaseModel, Field
#
# from app.common.geometries import Geometry
#
#
# with open("app/prioc/dto/example_territory.json", "r") as et:
#     example_territory = json.load(et)
#
#
# class IndicatorsDTO(BaseModel):
#     region_id: int = Field(..., examples=[1], description="The id of the territory")
#     potentials: bool = Field(..., examples=[True], description="Whether calculate territory potentials")
#     territory: Geometry = Field(..., examples=[example_territory], description="The territory polygon")
