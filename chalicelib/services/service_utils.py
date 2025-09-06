from typing import Optional, Callable
from chalicelib.repositories.base_repository import BaseRepository
from chalicelib.repositories.repository_factory import RepositoryFactory


def resolve_repo(
    provided: Optional[BaseRepository], factory_method: Callable[[], BaseRepository]
):
    return provided if provided is not None else factory_method()
