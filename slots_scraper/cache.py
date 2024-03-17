import pathlib
from typing import Type, TypeVar

from pydantic import BaseModel


TModel = TypeVar("TModel", bound=BaseModel)


class FileCache:
    def __init__(self, cache_dir: str = "/tmp"):
        self.cache_dir = pathlib.Path(cache_dir)

    def store(self, value: str, key: str) -> None:
        path = self._get_cache_filepath(key)
        path.write_text(value)

    def get(self, key: str) -> str | None:
        path = self._get_cache_filepath(key)

        if not path.exists():
            return None

        return path.read_text()

    def _get_cache_filepath(self, key: str) -> pathlib.Path:
        return (self.cache_dir / key).resolve()


class ModelStore:
    def __init__(self):
        self.prefix_mapping: dict[str, Type[TModel]] = {}

    def register_model_type(self, prefix: str,
                            model_type: Type[TModel]) -> None:
        self.prefix_mapping[prefix] = model_type

    def get_model_type(self, prefix: str) -> Type[TModel] | None:
        return self.prefix_mapping.get(prefix)

    def __setitem__(self, prefix: str, model_type: Type[TModel]) -> None:
        self.prefix_mapping[prefix] = model_type


class CacheManager:
    def __init__(self, cache: FileCache, model_store: ModelStore):
        self.cache = cache
        self.model_store = model_store

    def dump_model(self, model: TModel, key: str) -> None:
        json_data = model.model_dump_json()
        self.cache.store(json_data, key=key)

    def get_model_type(self, key: str) -> Type[TModel] | None:
        prefix = self._get_prefix_from_key(key)
        return self.model_store.prefix_mapping[prefix]

    def load_model_data(self, key) -> TModel | None:
        model = self.get_model_type(key=key)
        if cached := self.cache.get(key):
            return model.model_validate_json(cached)
        return None

    @staticmethod
    def _get_prefix_from_key(key: str) -> str:
        return key.split("_", 1)[0]
