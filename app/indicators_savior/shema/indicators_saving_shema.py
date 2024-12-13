from typing import Literal

from pydantic import BaseModel

class SaveResponse(BaseModel):

    msg: Literal[
        "Started indicators calculations and saving",
        "Successfully saved all indicators"
    ]
