from fastapi import APIRouter

from app.common import params_validator

limitations_router = APIRouter()


@limitations_router.get("/")
async def get_limitations(
        ids_only: bool = True,
) -> list[int] | list[dict[str, str | int]]:
    """
    Endpoint returns list of available ids to extract from

    ids_only: if true returns only ids. Defaults to true.
    """
    result = await params_validator.extract_current_regions(ids_only=ids_only)
    return result
