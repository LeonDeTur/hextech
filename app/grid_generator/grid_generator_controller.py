from fastapi import APIRouter

from .services import grid_generator_service


grid_generator_router = APIRouter(prefix="/grid_generator", tags=["Grid Generation"])

@grid_generator_router.get("/generate_to_db/{territory_id}")
async def generate_grid(territory_id: int):
    """
    Generate grid with provided territory id and save it to db

    Parameters:
        - territory_id (int): Territory ID

    Returns:
        - dict: Generated grid
    """

    result = await grid_generator_service.generate_grid_with_indicators_to_db(territory_id)
    return result
