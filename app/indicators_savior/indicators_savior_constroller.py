from typing import Annotated

from fastapi import APIRouter, Depends

from .dto import IndicatorsDTO
from .indicators_savior_service import indicators_savior_service


indicators_savior_router = APIRouter(prefix="/indicators_saving", tags=["Save all indicators to db"])


@indicators_savior_router.put("/save_all")
async def save_all_indicators_to_db(
        save_params: Annotated[IndicatorsDTO, Depends(IndicatorsDTO)]
):
    """
    Count all indicators and save them to db.
    """

    result = await indicators_savior_service.save_all_indicators(save_params)
    return result
