from typing import Annotated

from fastapi import APIRouter, Depends, BackgroundTasks
from loguru import logger

from app.common.exceptions.http_exception_wrapper import http_exception
from .dto import IndicatorsDTO
from .shema import SaveResponse
from .indicators_savior_service import indicators_savior_service


indicators_savior_router = APIRouter(prefix="/indicators_saving", tags=["Save all indicators to db"])


@indicators_savior_router.put("/save_all")
async def save_all_indicators_to_db(
        save_params: Annotated[IndicatorsDTO, Depends(IndicatorsDTO)],
        background_tasks: BackgroundTasks,
) -> SaveResponse:
    """
    Count all indicators and save them to db.
    """
    logger.info(f"""Started evaluating indicators with scenario id {save_params.scenario_id} 
    and territory id {save_params.territory_id}""")
    if save_params.territory_id != 1:
        raise http_exception(
            400,
            "Territories with id not equal to 1 are not currently supported.",
            _input=save_params.territory_id,
            _detail={"supported_ids": [1]}
        )

    if save_params.background:
        background_tasks.add_task(indicators_savior_service.save_all_indicators, save_params)
        return SaveResponse(**{"msg": "Started indicators calculations and saving"})
    result = await indicators_savior_service.save_all_indicators(save_params)
    return result
