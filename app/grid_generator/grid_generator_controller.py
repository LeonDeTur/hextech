import json

from fastapi import APIRouter

from .services import grid_generator_service


grid_generator_router = APIRouter(prefix="/hex_generator", tags=["Grid Generation"])


@grid_generator_router.post("/generate_full/{territory_id}")
async def generate_grid(territory_id: int) -> dict:
    """
    Generate grid with provided territory with indicators

    Parameters:

        - territory_id (int): Territory ID

    Returns:

        - dict: Generated grid with indicators
    """

    result = await grid_generator_service.generate_grid_with_indicators(
        territory_id,
        save_to_db=False
    )
    result = json.loads(result.to_json())
    return result

@grid_generator_router.post("/generate_to_db/{territory_id}")
async def generate_grid_to_db(territory_id: int) -> dict:
    """
    Generate grid with provided territory id and save it to db

    Parameters:

        - territory_id (int): Territory ID

    Returns:

        - dict: save massage with additional information
    """

    grid = await grid_generator_service.generate_grid(territory_id)
    result = await grid_generator_service.save_new_hexagons(
        territory_id,
        json.loads(grid.to_json())
    )
    return result

@grid_generator_router.get("/generate/{territory_id}")
async def generate_grid(territory_id: int) -> dict:
    """
    Generate grid with provided territory id, calculate all indicators and profiles potentials and save it to db

    Parameters:

        - territory_id (int): Territory ID
    """

    result = await grid_generator_service.generate_grid(territory_id)
    result = json.loads(result.to_json())
    return result
