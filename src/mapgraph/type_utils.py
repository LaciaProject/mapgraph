import types
import typing

from pydantic import TypeAdapter

from typing import (
    Union,
    List,
    Callable,
    Any,
    runtime_checkable,
    Type,
    get_origin,
    Optional,
)
from typing_extensions import get_type_hints, get_args
from typing_inspect import get_generic_type


def get_real_origin(tp):
    """Get the unsubscripted version of a type.

    This supports generic types, Callable, Tuple, Union, Literal, Final, ClassVar
    and Annotated. Return None for unsupported types. Examples::

        get_origin(Literal[42]) is Literal
        get_origin(int) is None
        get_origin(ClassVar[int]) is ClassVar
        get_origin(Generic) is Generic
        get_origin(Generic[T]) is Generic
        get_origin(Union[T, int]) is Union
        get_origin(List[Tuple[T, T]][int]) == List
        get_origin(P.args) is P
    """
    if isinstance(tp, typing._AnnotatedAlias):  # type: ignore
        return typing.Annotated
    if isinstance(tp, typing._GenericAlias):  # type: ignore
        if isinstance(tp._name, str) and getattr(typing, tp._name, None):
            return getattr(typing, tp._name)
        return tp.__origin__
    if isinstance(
        tp,
        (
            typing._BaseGenericAlias,  # type: ignore
            typing.GenericAlias,  # type: ignore
            typing.ParamSpecArgs,
            typing.ParamSpecKwargs,
        ),
    ):
        return tp.__origin__
    if tp is typing.Generic:
        return typing.Generic
    if isinstance(tp, types.UnionType):
        return types.UnionType
    return None


def is_structural_type(tp):
    if get_real_origin(tp):
        return True
    return False


def is_protocol_type(tp):
    return hasattr(tp, "_is_protocol") and tp._is_protocol


def is_generic_protocol_type(tp):
    return is_protocol_type(tp) and tp.__parameters__


def deep_type(obj, depth: int = 10, max_sample: int = -1):
    if depth <= 0:
        return get_generic_type(obj)
    if isinstance(obj, dict):
        keys = set()
        values = set()
        for k, v in obj.items():
            keys.add(deep_type(k, depth - 1, max_sample))
            values.add(deep_type(v, depth - 1, max_sample))
        if len(keys) == 1 and len(values) == 1:
            return dict[(*tuple(keys), *tuple(values))]  # type: ignore
        elif len(keys) > 1 and len(values) == 1:
            k_tpl = Union[tuple(keys)]  # type: ignore
            return dict[(k_tpl, *values)]  # type: ignore
        elif len(keys) == 1 and len(values) > 1:
            v_tpl = Union[tuple(values)]  # type: ignore
            return dict[(*keys, v_tpl)]  # type: ignore
        elif len(keys) > 1 and len(values) > 1:
            k_tpl = Union[tuple(keys)]  # type: ignore
            v_tpl = Union[tuple(values)]  # type: ignore
            return dict[(k_tpl, v_tpl)]  # type: ignore
        else:
            return dict
    elif isinstance(obj, list):
        args = set()
        for i in obj[::max_sample]:
            args.add(deep_type(i, depth - 1, max_sample))
        if len(args) == 1:
            return list[tuple(args)]  # type: ignore
        elif len(args) > 1:
            tpl = Union[tuple(args)]  # type: ignore
            return list[tpl]  # type: ignore
        else:
            return list
    elif isinstance(obj, tuple):
        args = []
        for i in obj:
            args.append(deep_type(i, depth - 1, max_sample))
        if len(args) >= 1:
            return tuple[tuple(args)]  # type: ignore
        else:
            return tuple
    else:
        res = get_generic_type(obj)
        if res in (type, typing._GenericAlias):  # type: ignore
            return Type[obj]
        return res


def get_generic_mapping(cls):
    # 用于存储最终的泛型变量和实际类型映射
    final_mapping = {}

    # 用于存储每一层的类型参数和实际类型的映射
    local_mappings = []

    def _resolve_generic(cls):
        args = get_args(cls)
        origin = get_origin(cls)

        if not args and hasattr(cls, "__orig_bases__"):
            # 如果类没有显式泛型参数，并且有原始基类，则解析原始基类
            for base in cls.__orig_bases__:
                _resolve_generic(base)
        else:
            type_vars = getattr(origin, "__parameters__", ())
            local_mapping = dict(zip(type_vars, args))
            local_mappings.append(local_mapping)

            # 递归解析基类
            for base in getattr(origin, "__orig_bases__", []):
                _resolve_generic(base)

    _resolve_generic(cls)

    # 将各层映射整合到最终映射中
    for mapping in reversed(local_mappings):
        for k, v in mapping.items():
            # 更新最终映射，确保泛型变量会映射到更具体的类型
            while v in final_mapping:
                v = final_mapping[v]
            final_mapping[k] = v

    return final_mapping


def attribute_check(
    tp,
    etp,
    tp_mapping: Optional[dict] = None,
    ex_mapping: Optional[dict] = None,
):
    from .typevar import check_typevar_model, gen_typevar_model

    htp = get_type_hints(tp, include_extras=True)
    hetp = get_type_hints(etp, include_extras=True)
    for key in hetp:
        if key not in htp:
            return False
        i, t = (
            htp[key]
            if tp_mapping is None
            else gen_typevar_model(htp[key]).get_instance(tp_mapping),
            hetp[key]
            if ex_mapping is None
            else gen_typevar_model(hetp[key]).get_instance(ex_mapping),
        )
        if not check_typevar_model(i, t):
            return False
    return True


def method_check(
    tp,
    etp,
    tp_mapping: Optional[dict] = None,
    ex_mapping: Optional[dict] = None,
):
    dhp = dir(tp)
    dehp = dir(etp)
    for key in dehp:
        if (key.startswith("__") and key.endswith("__")) or key.startswith("_"):
            continue
        if key not in dhp:
            return False
        if not attribute_check(
            getattr(tp, key), getattr(etp, key), tp_mapping, ex_mapping
        ):
            return False
    return True


def check_protocol_type(
    tp,
    expected_type,
    *,
    strict: bool = True,
    tp_mapping: Optional[dict] = None,
    ex_mapping: Optional[dict] = None,
):
    if not is_protocol_type(expected_type):
        raise TypeError(f"{expected_type} is not a protocol type")
    if strict:
        return attribute_check(
            tp, expected_type, tp_mapping, ex_mapping
        ) and method_check(tp, expected_type, tp_mapping, ex_mapping)
    return issubclass(tp, runtime_checkable(expected_type))


def generate_type(generic: Type[Any], instance: List[Type[Any]]):
    if types.UnionType == generic:
        return Union[tuple(instance)]  # type: ignore
    elif Callable == generic:
        if len(instance) == 2:
            return generic[instance[0], instance[1]]  # type: ignore
        return generic
    elif Optional == generic:
        NoneType = type(None)
        non_none_types = [i for i in instance if i != NoneType]
        if len(non_none_types) == 1:
            return Optional[non_none_types[0]]  # type: ignore
        else:
            raise ValueError("Optional requires a single type.")
    elif len(instance) == 0:
        return generic
    return generic[tuple(instance)]  # type: ignore


def iter_type_args(tp):
    args = tp.args
    if args:
        for arg in args:
            if isinstance(arg, list):
                for i in arg:
                    yield i
                    yield from iter_type_args(i)
            else:
                yield arg
                yield from iter_type_args(arg)


def like_issubclass(
    tp,
    expected_type,
    tp_mapping: Optional[dict] = None,
    ex_mapping: Optional[dict] = None,
):
    if tp == expected_type or expected_type == Any:
        return True
    try:
        if is_generic_protocol_type(expected_type):
            return check_protocol_type(
                tp, expected_type, tp_mapping=tp_mapping, ex_mapping=ex_mapping
            )
        elif is_protocol_type(expected_type):
            return check_protocol_type(tp, expected_type)
        elif issubclass(tp, expected_type):
            return True
    except TypeError:
        if get_origin(tp) == expected_type:
            return True
    return False


def like_isinstance(obj, expected_type):
    from .typevar import check_typevar_model

    res = False
    try:
        t = TypeAdapter(expected_type)
        t.validate_python(obj, strict=True)
        res = True
    except Exception:
        ...
    if res:
        return res
    if get_real_origin(expected_type) == Type:
        try:
            res = check_typevar_model(Type[obj], expected_type)
        except Exception:
            ...
    if res:
        return res
    
    obj_type = deep_type(obj)
    return check_typevar_model(obj_type, expected_type)
