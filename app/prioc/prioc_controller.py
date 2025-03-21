import json
from typing import Annotated

from loguru import logger
from fastapi import APIRouter, Depends

from .dto import HexesDTO, TerritoryDTO, prioc_objects_types
from .services import prioc_service


prioc_router = APIRouter(prefix="/prioc", tags=["Priority object calculation"])


@prioc_router.get("/prioc_objects_list")
async def get_prioc_objects_list():
    return prioc_objects_types

@prioc_router.get("/object")
# @decorators.gdf_to_geojson
async def get_object_hexes(
        hex_params: Annotated[HexesDTO, Depends(HexesDTO)]
) -> dict:
    """
    Calculate hexes to place priority objects with estimation value
    """

    logger.info(f"Starting /prioc/object with prams {hex_params.__dict__}")
    result = await prioc_service.get_hexes_for_object(hex_params)
    logger.info(f"Finished /prioc/object with prams {hex_params.__dict__}")
    return json.loads(result.to_json(to_wgs84=True))

@prioc_router.get("/cluster")
async def get_hexes_clusters(
        hex_params: Annotated[HexesDTO, Depends(HexesDTO)]
) -> dict:
    """
    Calculate hexes clusters to place priority objects with estimation value
    """

    logger.info(f"Starting /prioc/cluster with prams {hex_params.__dict__}")
    result = await prioc_service.get_hex_clusters_for_object(hex_params)
    logger.info(f"Finished /prioc/cluster with prams {hex_params.__dict__}")
    return json.loads(result.to_json(to_wgs84=True))

@prioc_router.post("/territory")
async def get_territory_value(
        territory_params: Annotated[TerritoryDTO, Depends(TerritoryDTO)],
) -> dict:
    """
    Calculate possible priority objects allocation
    """

    logger.info(f"Starting /prioc//territory with prams{territory_params.__dict__}")
    result = await prioc_service.get_territory_estimation(
        territory=territory_params.territory,
        territory_id=territory_params.territory_id,
    )
    logger.info(f"Finished /prioc/territory with prams {territory_params.__dict__}")
    return result
