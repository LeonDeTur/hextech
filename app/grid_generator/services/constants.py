from app.common.config.config import config
from app.common.storage.implementations.disposable_json import DisposableJSON


bucket_name = config.get("FILESERVER_BUCKET_NAME")
profile_weights_filename = config.get("FILESERVER_PROFILE_WEIGHTS")


profile_weights = DisposableJSON()
profile_weights.try_init(bucket_name, profile_weights_filename)
