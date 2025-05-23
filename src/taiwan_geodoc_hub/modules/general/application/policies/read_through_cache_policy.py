from typing import (
    Protocol,
    runtime_checkable,
    Awaitable,
    Generic,
    Callable,
    Optional,
    Union,
    TypeVar,
    Any,
)
from functools import wraps
from inspect import isawaitable
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
    UnitOfWork,
)

T = TypeVar("T", bound=Any)


@runtime_checkable
class Repository(Generic[T], Protocol):
    def load(self, key: str, /, unit_of_work: UnitOfWork) -> Optional[T]: ...
    def save(self, key: str, value: T, /, unit_of_work: UnitOfWork) -> None: ...


@runtime_checkable
class KeyComputer(Protocol):
    def __call__(self, *args, **kwargs) -> Union[str, Awaitable[str]]: ...


class ReadThroughCachePolicy(Generic[T]):
    _compute_key: KeyComputer
    _unit_of_work: UnitOfWork
    _repository: Repository[T]

    def __init__(
        self,
        /,
        compute_key: KeyComputer,
        unit_of_work: UnitOfWork,
        repository: Repository[T],
    ):
        self._compute_key = compute_key
        self._unit_of_work = unit_of_work
        self._repository = repository

    def __call__(
        self,
        callable: Callable[..., Awaitable[T]],
    ):
        @wraps(callable)
        async def wrapped(*args, **kwargs):
            async with self._unit_of_work as unit_of_work:
                key: str
                result = self._compute_key(*args, **kwargs)
                if isawaitable(result):
                    key = await result
                else:
                    key = result
                hit = await self._repository.load(key, unit_of_work=unit_of_work)
                if hit is not None:
                    return hit

                data = await callable(*args, **kwargs)
                await self._repository.save(key, data, unit_of_work=unit_of_work)
                return data

        return wrapped
