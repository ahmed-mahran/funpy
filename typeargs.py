"""
Capturing types of Variadic Generics.

A workaround for `type[*Ts]`:
>>> def fn[*Ts](args: type[*Ts]) -> tuple[*Ts]: ...

E.g. How to rewrite `fn` to return `tuple[int, str]` istead of `tuple[type[int], type[str]]`
>>> def fn[*Ts](*args: *Ts) -> tuple[*Ts]: ...

>>> reveal_type(fn(int, str)) # tuple[type[int], type[str]]
"""
from __future__ import annotations

from typing import reveal_type

##### Problem
def fn1[*Ts](*args: *Ts) -> tuple[*Ts]: ...
reveal_type(fn1(int, str))  # tuple[type[int], type[str]]


##### TypeArgs workaround
class Args[*Ts]: pass
type TypeArgs[*Ts] = type[Args[*Ts]]

def fn2[*Ts](*args: TypeArgs[*Ts]) -> tuple[*Ts]: ...
reveal_type(fn2(Args[int, str]))  # tuple[int, str]


##### Callable objects workaround
class fn3[*Ts]:
    def __call__(self) -> tuple[*Ts]: ...
reveal_type(fn3[int, str]()()) # tuple[int, str]


##### Tuple extension workaround
class fn4[*Ts](tuple[*Ts]):
    def __new__(cls) -> tuple[*Ts]: ...
x4: tuple[int, str] = fn4[int, str]() # Accepted
reveal_type(fn4[int, str]()) # tuple[int, str]
