from typing import Optional, TypeVar

T = TypeVar('T')

def zip_or(xs: list[Optional[T]], ys: list[Optional[T]]) -> list[Optional[T]]:
    return [x or y for x, y in zip(xs, ys)]
