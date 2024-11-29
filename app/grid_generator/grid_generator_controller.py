from fastapi import APIRouter


grid_generator_router = APIRouter(prefix="/grid_generator", tags=["Grid Generation"])

@grid_generator_router.get("/generate")
async def generate_grid(territory_id: int):
    """
    Generate grid with provided territory id
    """

    pass
