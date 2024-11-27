import pytest

from app.routers.prioc.services.hex_api_service import hex_api_getter
from app.routers.prioc.services.hex_cleaner import hex_cleaner


@pytest.mark.asyncio
async def test_get_hexes_with_indicators_by_territory():
    hexes = await hex_api_getter.get_hexes_with_indicators_by_territory(1)
    assert len(hexes) == 2148

@pytest.mark.asyncio
async def test_():
    positive_services = await hex_api_getter.get_positive_service_by_territory_id(
        territory_id=1,
        service_type_ids=[6]
    )
    assert len(positive_services) == 0

@pytest.mark.asyncio
async def test_get_negative_service_by_territory_id():
    negative_services = await hex_api_getter.get_negative_service_by_territory_id(
        territory_id=1,
        service_type_ids=[112, 143]
    )
    assert len(negative_services) == 194

@pytest.mark.asyncio
async def test_negative_clean():
    hexes = await hex_api_getter.get_hexes_with_indicators_by_territory(1)
    negative_services = await hex_api_getter.get_negative_service_by_territory_id(
        territory_id=1,
        service_type_ids=[112, 143]
    )
    cleaned = await hex_cleaner.negative_clean(
        hexes,
        negative_services
    )
    assert len(cleaned) < len(hexes)

@pytest.mark.asyncio
async def test_positive_clean():
    hexes = await hex_api_getter.get_hexes_with_indicators_by_territory(1)
    positive_services = await hex_api_getter.get_positive_service_by_territory_id(
        territory_id=1,
        service_type_ids=[6]
    )
    cleaned = await hex_cleaner.negative_clean(hexes, positive_services)
    assert len(cleaned) == len(hexes)
