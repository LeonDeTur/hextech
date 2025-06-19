import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, BackgroundTasks
from loguru import logger

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
    logger.info(f"""Started evaluating indicators with scenario id {save_params.project_id} 
    and scenario id {save_params.scenario_id}""")

    await asyncio.sleep(30)
    if save_params.background:
        logger.info(f"Started background tasks for indicators with scenario params {save_params.__dict__}")
        background_tasks.add_task(indicators_savior_service.save_all_indicators, save_params)
        return SaveResponse(**{"msg": "Started indicators calculations and saving"})
    result = await indicators_savior_service.save_all_indicators(save_params)
    return result
