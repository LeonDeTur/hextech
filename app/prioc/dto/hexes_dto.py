from pydantic import BaseModel, Field
from typing import Literal


prioc_objects_types = [
        "Медицинский комплекс",
        "Бизнес-кластер",
        "Пром объект",
        "Логистическо-складской комплекс",
        "Порт",
        "Кампус университетский",
        "Тур база",
    ]


class HexesDTO(BaseModel):

    territory_id: int = Field(
        ...,
        examples=[1],
        description="Territory id to calculate hexes priority"
    )

    object_type: prioc_objects_types = Field(
        ...,
        examples=["Тур база"],
        description="Possible object to place in territory"
    )
