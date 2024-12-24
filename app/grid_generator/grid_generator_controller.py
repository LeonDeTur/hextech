import json

from fastapi import APIRouter
from loguru import logger

from .services import grid_generator_service


grid_generator_router = APIRouter(prefix="/hex_generator", tags=["Grid Generation"])


@grid_generator_router.get("/generate_full/{territory_id}")
async def generate_grid_with_indicators_and_potentials(territory_id: int) -> dict:
    """
    Generate grid with provided territory with indicators

    Parameters:

        - territory_id (int): Territory ID

    Returns:

        - dict: Generated grid with indicators
    """
    logger.info(f"Started /hex_generator/generate_full/{territory_id}")
    result = await grid_generator_service.generate_grid_with_indicators(
        territory_id,
    )
    result = json.loads(result.to_json())
    logger.info(f"Finished /hex_generator/generate_full/{territory_id}")
    return result

@grid_generator_router.put("/bound_indicators_to_hexes/{territory_id}")
async def bound_indicators_to_hexes(territory_id: int) -> dict:
    """
    Calculate and bound indicators to hexes in db
    """

    logger.info(f"Started /hex_generator/bound_indicators_to_hexes/{territory_id}")
    result = await grid_generator_service.bound_hexagons_indicators(
        territory_id,
    )
    logger.info(f"Finished /hex_generator/bound_indicators_to_hexes/{territory_id}")
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

    logger.info(f"Started /hex_generator/generate_to_db/{territory_id}")
    grid = await grid_generator_service.generate_grid(territory_id)
    result = await grid_generator_service.save_new_hexagons(
        territory_id,
        json.loads(grid.to_json())
    )
    logger.info("Finished /hex_generator/generate_to_db/{territory_id}")
    return result

@grid_generator_router.get("/generate/{territory_id}")
async def generate_grid(territory_id: int) -> dict:
    """
    Generate grid with provided territory id, calculate all indicators and profiles potentials and save it to db

    Parameters:

        - territory_id (int): Territory ID
    """

    logger.info(f"Started /hex_generator/generate/{territory_id}")
    result = await grid_generator_service.generate_grid(territory_id)
    result = json.loads(result.to_json())
    logger.info(f"Finished /hex_generator/generate/{territory_id}")
    return result
