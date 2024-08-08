"""
Type transformation on Variadic Generics
"""
from __future__ import annotations

from typing import Callable, cast, reveal_type

type Identity[X] = X


class Mapped[F, *Ts](tuple):
    """
    Holds elements of type F[T] such that T belongs to set of types Ts.

    >>> Mapped[F, *Ts] = {F[T]; ∀ T ∈ Ts}
    """

    def flatmap[F2](self, f2: Callable[[F], F2]) -> Mapped[F2, *Ts]:
        return Functor(f2)(*self)  # type: ignore

    @staticmethod
    def identity[*Is](*args: *Is) -> Mapped[Identity, *Is]:
        return Mapped[Identity, *Is](args)


class Functor[F, T]:
    """
    Functor applies a map/transformation F on elements of type T
    such that T belongs to set of types Ts.

    The set of mapped/transformed elements is Mapped[F, *Ts].
    """

    def __init__(self, map: Callable[[T], F]):
        self.map = map

    def __call__[*Ts](self, *ts: *Ts) -> Mapped[F, *Ts]:
        return Mapped[F, *Ts](tuple([self.map(cast(T, t)) for t in ts]))


class FlatMap[FIn, FOut]:
    """
    Applies a transformation FOut on transformed elements Mapped[FIn, Ts].
    The result is Mapped[FOut, *Ts].
    
    >>> Mapped[FOut, *Ts] = {f_out(f_in_t); ∀ f_in_t ∈ Mapped[FIn, *Ts]}
    >>> f_in_t is of type FIn[T]
    >>> f_out(f_in_t) is of type FOut[T]
    """
    def __init__(self, f_out: Callable[[FIn], FOut]) -> None:
        self.functor = Functor[FOut, FIn](f_out)

    def __call__[*Ts](self, t: Mapped[FIn, *Ts]) -> Mapped[FOut, *Ts]:
        return self.functor(*t)  # type: ignore


t0 = Mapped.identity(1, "1")
reveal_type(t0)   # Pylance: Mapped[Identity[Unknown], int, str]
                  # Pycharm: Mapped[X, int, str]
                  # mypy: Any
print(t0)  # (1, '1')


def f1(x) -> list:
    return [x]


# t1 = Functor(lambda x: [x])(1, "1")
# t1 = t0.flatmap(lambda x: [x])
t1 = t0.flatmap(f1)
reveal_type(t1)   # Pylance: Mapped[list[Unknown], int, str]
                  # Pycharm: Mapped[list, int, str]
                  # mypy: Any
print(t1)  # ([1], ['1'])


def f2(x: list) -> type:
    return type(x[0])


# t2 = t1.flatmap(lambda x: type(x[0]))
t2 = t1.flatmap(f2)
reveal_type(t2)   # Pylance: Mapped[type[Unknown], int, str]
                  # Pycharm: Mapped[type, int, str]
                  # mypy: Any
print(t2)  # (<class 'int'>, <class 'str'>)

t2_again = FlatMap(f2)(t1)
reveal_type(t2_again)   # Pylance: Mapped[type, int, str]
                        # Pycharm: Any
                        # mypy: Mapped[builtins.type, Unpack[builtins.tuple[Any, ...]]]
print(t2_again)  # (<class 'int'>, <class 'str'>)
