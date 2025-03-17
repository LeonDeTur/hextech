# import json
# from typing import Annotated
#
# from fastapi import APIRouter, Depends
#
# from .dto import IndicatorsDTO
# from app.grid_generator.services import grid_generator_service
#
#
# potential_indicator_router = APIRouter(prefix="/potential_indicator", tags=["Potential calculation"])
#
# @potential_indicator_router.post("{territory_id}/calculate")
# async def calculate_potential_indicator(
#     indicators_params: Annotated[IndicatorsDTO, Depends(grid_generator_service)]
# ):
#     """
#     Get indicators and potentials for territory
#     """

