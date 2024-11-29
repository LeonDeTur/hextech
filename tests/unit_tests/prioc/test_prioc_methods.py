import pytest
import statistics

from fastapi import HTTPException
from shapely.geometry import shape
import geopandas as gpd

from app.common import urban_api_handler, config
from app.prioc.services.hex_api_service import hex_api_getter
from app.prioc.services.hex_cleaner import hex_cleaner
from app.prioc.services.hex_estimator import hex_estimator
from app.prioc.services.territory_estimator import territory_estimator
from app.prioc.services.prioc_service import prioc_service
from app.prioc.dto import HexesDTO, TerritoryDTO
from app.common.geometries import example_territory


@pytest.mark.asyncio
async def test_get_hexes_with_indicators_by_territory():
    hexes = await hex_api_getter.get_hexes_with_indicators_by_territory(1)
    assert isinstance(hexes, gpd.GeoDataFrame)
    assert len(hexes) == 2148

@pytest.mark.asyncio
async def test_exception_get_hexes_with_indicators_by_territory():
    try:
        await hex_api_getter.get_hexes_with_indicators_by_territory(-1)
        assert False
    except:
        assert True

@pytest.mark.asyncio
async def test_get_positive_service_by_territory_id():
    positive_services = await hex_api_getter.get_positive_service_by_territory_id(
        territory_id=1,
        service_type_ids=[6]
    )
    assert len(positive_services) == 0

@pytest.mark.asyncio
async def test_not_none_positive_service_by_territory_id():
    positive_services = await hex_api_getter.get_positive_service_by_territory_id(
        territory_id=1,
        service_type_ids=[112]
    )
    assert len(positive_services) > 0

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
    print(len(negative_services), hexes.crs, negative_services.crs)
    cleaned = await hex_cleaner.negative_clean(
        hexes,
        negative_services
    )
    assert len(cleaned) < len(hexes)

@pytest.mark.asyncio
async def test_negative_empty_clean():
    hexes = await hex_api_getter.get_hexes_with_indicators_by_territory(1)
    negative_services = gpd.GeoDataFrame()
    cleaned = await hex_cleaner.negative_clean(
        hexes,
        negative_services
    )
    assert len(cleaned) == len(hexes)

@pytest.mark.asyncio
async def test_positive_empty_clean():
    hexes = await hex_api_getter.get_hexes_with_indicators_by_territory(1)
    positive_services = await hex_api_getter.get_positive_service_by_territory_id(
        territory_id=1,
        service_type_ids=[6]
    )
    print(positive_services)
    cleaned = await hex_cleaner.positive_clean(hexes, positive_services)
    assert len(cleaned) == len(hexes)

@pytest.mark.asyncio
async def test_positive_clean():
    hexes = await hex_api_getter.get_hexes_with_indicators_by_territory(1)
    positive_services = await hex_api_getter.get_positive_service_by_territory_id(
        territory_id=1,
        service_type_ids=[112, 143]
    )
    print(positive_services.columns)
    cleaned = await hex_cleaner.positive_clean(hexes, positive_services)
    assert len(cleaned) < len(hexes)

@pytest.mark.asyncio
async def test_clean_estimation_dict_by_territory():
    territory = gpd.GeoDataFrame(geometry=[shape(example_territory)], crs=4326)
    positive_services = territory.copy()
    negative_services = territory.copy()
    positive = await hex_cleaner.clean_estimation_dict_by_territory(
        territory=territory,
        positive_services=positive_services,
        negative_services=None,
    )
    negative = await hex_cleaner.clean_estimation_dict_by_territory(
        territory=territory,
        positive_services=None,
        negative_services=negative_services,
    )
    print(positive)
    print(negative)
    assert positive == True
    assert negative == True

@pytest.mark.asyncio
async def test_weight_hexes():
    hexes = await hex_api_getter.get_hexes_with_indicators_by_territory(1)
    weighted_hexes = await hex_estimator.weight_hexes(hexes, "Тур база")
    check_result = round(weighted_hexes["weighted_sum"].mean(), 2)
    assert check_result == 2.21

@pytest.mark.asyncio
async def test_clarify_clusters():
    hexes = await hex_api_getter.get_hexes_with_indicators_by_territory(1)
    hexes = hexes[:100].copy()
    hexes["cluster"] = [1 for i in range(50)] + [2 for i in range(50)]
    hexes["X"] = None
    hexes["Y"] = None
    cleaned_hexes = await hex_estimator.clarify_clusters(hexes)
    assert len(cleaned_hexes) == 2

@pytest.mark.asyncio
async def test_cluster_hexes():
    hexes = await hex_api_getter.get_hexes_with_indicators_by_territory(1)
    hexes = hexes[:300].copy()
    wighted_hexes = await hex_estimator.weight_hexes(hexes, "Тур база")
    clustered_hexes = await hex_estimator.cluster_hexes(wighted_hexes)
    clustered_num = len(clustered_hexes[clustered_hexes["cluster"] != -1])
    assert clustered_num > 0

@pytest.mark.asyncio
async def test_estimate_territory():
    hexes = await hex_api_getter.get_hexes_with_indicators_by_territory(1)
    territory = gpd.GeoDataFrame(geometry=[shape(example_territory)], crs=4326)
    territory_hexagons = hexes.clip(territory.geometry)
    result = await territory_estimator.estimate_territory(territory_hexagons)
    mean = round(
        statistics.mean(
            [list(result[key]["estimation"])[0] for key in result.keys()]
        ),
        2
    )
    assert mean == 0.92

@pytest.mark.asyncio
async def test_get_hexes_for_object():
    test_hex_dto = HexesDTO(
        territory_id=1,
        object_type="Тур база"
    )

    result = await prioc_service.get_hexes_for_object(test_hex_dto)
    assert len(result) == 39

@pytest.mark.asyncio
async def test_get_hexes_for_object_positive_services():
    test_hex_dto = HexesDTO(
        territory_id=1,
        object_type="Порт"
    )

    result = await prioc_service.get_hexes_for_object(test_hex_dto)
    assert len(result) == 351

@pytest.mark.asyncio
async def test_get_hex_clusters_for_object():
    test_hex_dto = HexesDTO(
        territory_id=1,
        object_type="Тур база"
    )
    result = await prioc_service.get_hex_clusters_for_object(test_hex_dto)
    result = result[result["cluster"] != -1]
    assert len(result) > 0

@pytest.mark.asyncio
async def test_get_territory_estimation():
    test_territory_dto = TerritoryDTO(
        territory_id=1,
        territory=example_territory
    )
    result = await prioc_service.get_territory_estimation(test_territory_dto)
    mean = round(
        statistics.mean(
            [list(result[key]["estimation"])[0] for key in result.keys()]
        ),
        2
    )
    assert mean == 1.02

@pytest.mark.asyncio
async def test_get():
    try:
        url = "/api/v1/territory/geojson?territory_id=-1"
        await urban_api_handler.get(url, params={})
        assert False
    except HTTPException as e:
        assert e.status_code == 422
