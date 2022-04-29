from typing import Callable, Iterable, Optional, TypeVar, Any

T = TypeVar('T')
U = TypeVar('U')

def zip_or(xs: list[Optional[T]], ys: list[Optional[T]]) -> list[Optional[T]]:
    return [x or y for x, y in zip(xs, ys)]

def compact(xs: list[Optional[T]]) -> list[T]:
    return [x for x in xs if x]

def uncompact(xs: list[T], pattern: list[Optional[Any]]) -> list[Optional[T]]:
    it = iter(xs)
    ys = []
    for p in pattern:
        ys.append(next(it) if p else None)
    return ys

def with_compact(f: Callable[[list[T]], Iterable[U]], xs: list[Optional[T]]) -> list[Optional[U]]:
    return uncompact(list(f(compact(xs))), xs)
