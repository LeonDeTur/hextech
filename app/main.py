import sys
from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .common.config import config
from .prioc import prioc_router
from .grid_generator import grid_generator_router
from .limitations import limitations_router
from .indicators_savior import indicators_savior_router


logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:MM-DD HH:mm}</green> | <level>{level:<8}</level> | <cyan>{message}</cyan>",
    level="INFO",
    colorize=True
)
logger.add(
    ".log", colorize=False, backtrace=True, diagnose=True
)

app = FastAPI(
    title="hextech",
    description="API for spatial hexagonal analyses"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/logs")
async def get_logs():
    """
    Get app logs
    """

    return FileResponse(
        ".log",
        media_type='application/octet-stream',
        filename=f"Hextech.log",
    )

app.include_router(prioc_router, prefix=config.get("FASTAPI_PREFIX"))
app.include_router(grid_generator_router, prefix=config.get("FASTAPI_PREFIX"))
app.include_router(limitations_router, prefix=config.get("FASTAPI_PREFIX"))
app.include_router(indicators_savior_router, prefix=config.get("FASTAPI_PREFIX"))


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")
