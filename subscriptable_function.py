from __future__ import annotations

from typing import Callable, Concatenate, Tuple, Type, reveal_type

args = ()
kwargs = {}

#######################################
#             functions               #
#######################################

#----------------------------------#
#           workarounds            #
#----------------------------------#

# double parentheses to call: fn1[int, str]()()
# type arguments can be captured from self.__orig_class__.__args__
class fn1[A, B]:
    def __call__(self, *args, **kwargs) -> Tuple[A, B]: ...


reveal_type(fn1[int, str]()(*args, **kwargs))  # Tuple[int, str]


# parentheses to call: fn2[int, str]()
# type arguments cannot be captured from self.__orig_class__.__args__
class fn2[A, B]:
    def __new__(cls, *args, **kwargs) -> Tuple[A, B]: ...


reveal_type(fn2[int, str](*args, **kwargs))  # Tuple[int, str]


# no parentheses/call arguments
# no parentheses to call: fn3[int, str]
# type arguments can be captured from tp
class fn3:
    def __class_getitem__[A, B](cls, tp: Tuple[Type[A], Type[B]]) -> Tuple[A, B]: ...


reveal_type(fn3[int, str])  # type[fn3] <-- static type inference failure


# parentheses to call: fn4[int, str]()
# type arguments can be captured from tp
class fn4:
    def __class_getitem__[A, B](cls, tp: Tuple[Type[A], Type[B]]) -> Callable[[], Tuple[A, B]]:
        def inner(*args, **kwargs) -> Tuple[A, B]:
            ...
        return inner


reveal_type(fn4[int, str](*args, **kwargs))  # fn4 <-- static type inference failure


# parentheses to call: fn5[int, str]()
# type arguments can be captured from tp
class _fn5:
    def __getitem__[A, B](self, tp: Tuple[Type[A], Type[B]]) -> Callable[[], Tuple[A, B]]:
        def inner(*args, **kwargs) -> Tuple[A, B]:
            ...
        return inner

fn5 = _fn5()

reveal_type(fn5[int, str](*args, **kwargs))  # Tuple[int, str]


# no parentheses/call arguments
# no parentheses to call: fn6[int, str]
# type arguments can be captured from tp
class _fn6:
    def __getitem__[A, B](self, tp: Tuple[Type[A], Type[B]]) -> Tuple[A, B]:
        ...

fn6 = _fn6()

reveal_type(fn6[int, str])  # Tuple[int, str]

#----------------------------------#
#              utils               #
#----------------------------------#

class Args[*T]: pass
type TypeArgs[*T] = type[Args[*T]]

class subscriptable[*T, **P, R]:
    def __init__(self, fn: Callable[Concatenate[TypeArgs[*T], P], R]) -> None:
        self.fn = fn

    def __getitem__(self, tp: TypeArgs[*T]) -> Callable[P, R]:
        def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            return self.fn(tp, *args, **kwargs)
        # functools.wraps
        inner.__type_params__ = (T,)
        return inner


@subscriptable
def fun1[A, B](tp: TypeArgs[A, B], a: A, b: B) -> Tuple[A, B]:
    ...

reveal_type(fun1) # subscriptable[A@fun1, B@fun1, (a: A@fun1, b: B@fun1), Tuple[A@fun1, B@fun1]]
# Argument of type "type[Args[int, str]]" cannot be assigned to parameter "tp" of type "TypeArgs[A@fun1, B@fun1]" in function "__getitem__"
#   "type[Args[int, str]]" is incompatible with "TypeArgs[A@fun1, B@fun1]"
#   Type "type[Args[int, str]]" is incompatible with type "TypeArgs[A@fun1, B@fun1]"
#     Type parameter "T@Args" is covariant, but "*tuple[int, str]" is not a subtype of "*tuple[A@fun1, B@fun1]"
#       "*tuple[int, str]" is incompatible with "*tuple[A@fun1, B@fun1]"
#         Tuple entry 1 is incorrect type
#           Type "int" is incompatible with type "A@fun1"
reveal_type(fun1[Args[int, str]]) # (a: A@fun1, b: B@fun1) -> Tuple[A@fun1, B@fun1]
reveal_type(fun1[Args[int, str]]('a', 1)) # Tuple[str, int]

class subscriptable1[T, **P, R]:
    def __init__(self, fn: Callable[Concatenate[Type[T], P], R]) -> None:
        self.fn = fn

    def __getitem__(self, tp: Type[T]) -> Callable[P, R]:
        def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            return self.fn(tp, *args, **kwargs)
        # functools.wraps
        inner.__type_params__ = (T,)
        return inner


@subscriptable1
def fun2[A](tp: Type[A], a: A) -> Tuple[A]:
    ...

reveal_type(fun2) # subscriptable1[A@fun2, (a: A@fun2), Tuple[A@fun2]]
# Argument of type "type[int]" cannot be assigned to parameter "tp" of type "type[A@fun2]" in function "__getitem__"
#  Type "type[int]" is incompatible with type "type[A@fun2]"
reveal_type(fun2[int]) # (a: A@fun2) -> Tuple[A@fun2]
reveal_type(fun2[int]('a')) # Tuple[str]




#######################################
#              methods                #
#######################################

#----------------------------------#
#           workarounds            #
#----------------------------------#

# no parentheses/call arguments
# no parentheses to call: Owner1().fn[int, str]
# type arguments can be captured from tp
class Owner1:
    class _fn:
        def __init__(self, owner: Owner1) -> None:
            self.owner = owner

        def __getitem__[A, B](self, tp: Tuple[Type[A], Type[B]]) -> Tuple[A, B]: ...

    @property
    def fn(self):
        return Owner1._fn(self)


reveal_type(Owner1().fn[int, str])  # Tuple[int, str]


# parentheses to call: Owner2().fn[int, str]()
# type arguments can be captured from tp
class Owner2:
    class _fn:
        def __init__(self, owner: Owner2) -> None:
            self.owner = owner

        def __getitem__[A, B](self, tp: Tuple[Type[A], Type[B]]):
            def inner(*args, **kwargs) -> Tuple[A, B]: ...

            return inner

    @property
    def fn(self):
        return Owner2._fn(self)


reveal_type(Owner2().fn[int, str](*args, **kwargs))  # Tuple[int, str]


#----------------------------------#
#              utils               #
#----------------------------------#


class subscriptablemethod[Self, *T, **P, R]:
    def __init__(self, fn: Callable[Concatenate[Self, TypeArgs[*T], P], R]) -> None:
        self.fn = fn

    def __get__(self, instance: Self, owner: Type[Self]):
        self.instance = instance
        return self

    def __getitem__(self, tp: TypeArgs[*T]) -> Callable[P, R]:
        def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            return self.fn(self.instance, tp, *args, **kwargs)
        # functools.wraps
        inner.__type_params__ = (T,)
        return inner
    
class Owner3:
    @subscriptablemethod
    def fn[A, B](self, tp: TypeArgs[A, B], a: A, b: B) -> Tuple[A, B]:
        ...

reveal_type(Owner3().fn) # subscriptablemethod[Owner3, A@fn, B@fn, (a: A@fn, b: B@fn), Tuple[A@fn, B@fn]]
# Argument of type "type[Args[int, str]]" cannot be assigned to parameter "tp" of type "TypeArgs[A@fn, B@fn]" in function "__getitem__"
#   "type[Args[int, str]]" is incompatible with "TypeArgs[A@fn, B@fn]"
#   Type "type[Args[int, str]]" is incompatible with type "TypeArgs[A@fn, B@fn]"
#     Type parameter "T@Args" is covariant, but "*tuple[int, str]" is not a subtype of "*tuple[A@fn, B@fn]"
#       "*tuple[int, str]" is incompatible with "*tuple[A@fn, B@fn]"
#         Tuple entry 1 is incorrect type
#           Type "int" is incompatible with type "A@fn"
reveal_type(Owner3().fn[Args[int, str]]) # (a: A@fn, b: B@fn) -> Tuple[A@fn, B@fn]
reveal_type(Owner3().fn[Args[int, str]]('a', 1)) # Tuple[str, int]
