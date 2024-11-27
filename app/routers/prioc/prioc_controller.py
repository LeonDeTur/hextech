import json
from typing import Annotated

from fastapi import APIRouter, Depends

from .dto import HexesDTO, TerritoryDTO
from .services.prioc_service import prioc_service


prioc_router = APIRouter(prefix="/prioc", tags=["Priority object calculation"])


@prioc_router.get("/object")
# @decorators.gdf_to_geojson
async def get_object_hexes(
        hex_params: Annotated[HexesDTO, Depends(HexesDTO)]
) -> dict:
    """
    Calculate hexes to place priority objects with estimation value
    """

    result = await prioc_service.get_hexes_for_object(hex_params)
    return json.loads(result.to_json(to_wgs84=True))

@prioc_router.get("/cluster")
async def get_hexes_clusters(
        hex_params: Annotated[HexesDTO, Depends(HexesDTO)]
) -> dict:
    """
    Calculate hexes clusters to place priority objects with estimation value
    """

    result = await prioc_service.get_hex_clusters_for_object(hex_params)
    return json.loads(result.to_json(to_wgs84=True))

@prioc_router.post("/territory")
async def get_territory_value(
        territory_params: TerritoryDTO
) -> dict:
    """
    Calculate possible priority objects allocation
    """

    result = await prioc_service.get_territory_estimation(territory_params)
    return result
