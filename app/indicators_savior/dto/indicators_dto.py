import json
from typing import Literal

from pydantic import BaseModel, Field

from app.common.geometries import Geometry


with open("app/prioc/dto/example_territory.json", "r") as et:
    example_territory = json.load(et)


class IndicatorsDTO(BaseModel):

    project_id: int = Field(
        ...,
        examples=[72]
    )
    scenario_id: int = Field(
        ...,
        examples=[128],
        description="Scenario to create or update indicators for"
    )
    background: bool = Field(...,
                             examples=[False],
                             description="If 'true' calculates in background"
                             )
