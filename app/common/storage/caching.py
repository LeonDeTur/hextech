from pathlib import Path
from datetime import datetime

from app.common.config.config import config
from app.common.storage.interfaces import Cacheable
from app.common.exceptions.http_exception_wrapper import http_exception


class CachingService:
    def __init__(self, cache_path: Path):
        self.cache_actuality_hours = int(config.get("CACHE_ACTUALITY_HOURS"))
        self.cache_path = cache_path
        self.cache_path.mkdir(parents=True, exist_ok=True)

    def save(self, cacheable: Cacheable, name: str, date: datetime, *args) -> None:
        cacheable.to_file(self.cache_path, name, date, *args)

    def get_cached_file_name(self, name: str) -> str:
        # Get list of files with pattern *{name}
        files = [file.name for file in self.cache_path.glob(f"*{name}")]
        if len(files) == 0:
            return ""
        elif len(files) > 1:
            raise http_exception(
                500,
                "Several instances of file in cache directory, manual conflict resolution required",
                [name, len(files)],
                _detail="get_cached_file_name",
            )

        # Only 1 instance of file can be in cache directory
        file = files[0]
        return file

    def get_file_meta(self, name: str) -> str:
        file = self.get_cached_file_name(name)

        # Save format is {date}_{name}
        # Split with "_" with always result in {date} in position 0
        file_creation_date = file.split("_")[0]
        return file_creation_date

caching_service = CachingService(Path().absolute() / config.get("CACHE_NAME"))
