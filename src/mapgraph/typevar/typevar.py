from __future__ import annotations
from typing import TypeVar, List, Type, Any, Optional, Union
import types
from dataclasses import dataclass
from collections import deque

from typing_extensions import get_args
from typing_inspect import is_typevar, is_generic_type, get_bound, get_constraints

from ..type_utils import (
    get_real_origin,
    generate_type,
    like_issubclass,
    is_generic_protocol_type,
    get_generic_mapping,
)

In = TypeVar("In", contravariant=True)


@dataclass
class TypeVarModel:
    origin: Any
    args: Optional[List["TypeVarModel" | List["TypeVarModel"]]] = None

    def to_dict(self):
        return {
            "origin": self.origin,
            "args": [
                arg.to_dict() if isinstance(arg, TypeVarModel) else arg
                for arg in self.args
            ]
            if self.args is not None
            else self.args,
        }

    def get_instance(self, instance: Optional[dict[Type[TypeVar], Type]] = None):
        generic = self.origin
        args_list = []
        if instance is None:
            instance = {}
        if self.args is None or not self.args:
            if is_typevar(generic):
                return instance.get(generic, generic)
            return generic

        for arg in self.args:
            if isinstance(arg, TypeVarModel):
                args_list.append(arg.get_instance(instance))
            elif isinstance(arg, list):
                args_list.append([a.get_instance(instance) for a in arg])
            else:
                raise ValueError("Invalid TypeVarModel")
        return generate_type(generic, args_list)

    def replace_args(
        self, source: TypeVarModel, target: TypeVarModel
    ) -> "TypeVarModel":
        if self.args is None:
            return TypeVarModel(self.origin)

        new_args = []
        for arg in self.args:
            if isinstance(arg, TypeVarModel):
                if arg == source:
                    new_args.append(target)
                else:
                    new_args.append(arg.replace_args(source, target))
            elif isinstance(arg, list):
                new_list = []
                for item in arg:
                    if isinstance(item, TypeVarModel):
                        if item == source:
                            new_list.append(target)
                        else:
                            new_list.append(item.replace_args(source, target))
                    else:
                        new_list.append(item)
                new_args.append(new_list)
            else:
                new_args.append(arg)

        return TypeVarModel(self.origin, new_args)

    def depth_first_traversal(self, parent=None, parent_arg_index=None, depth=1):
        if self.args:
            for i, arg in enumerate(self.args):
                if isinstance(arg, TypeVarModel):
                    yield from arg.depth_first_traversal(self, i, depth + 1)
                elif isinstance(arg, list):
                    for j, a in enumerate(arg):
                        if isinstance(a, TypeVarModel):
                            yield from a.depth_first_traversal(self, (i, j), depth + 1)
            yield self, parent, parent_arg_index, depth
        else:
            yield self, parent, parent_arg_index, depth

    def remove_deepest_level_node(self):
        max_depth = self.get_max_depth()
        deepest_nodes_info = []

        for node, parent, parent_arg_index, depth in self.depth_first_traversal():
            if depth == max_depth:
                deepest_nodes_info.append((node, parent, parent_arg_index))

        for _, parent, parent_arg_index in reversed(deepest_nodes_info):
            if isinstance(parent_arg_index, tuple):
                list_index, item_index = parent_arg_index
                if list_index < len(parent.args) and item_index < len(
                    parent.args[list_index]
                ):
                    parent.args[list_index].pop(item_index)
            else:
                if parent_arg_index < len(parent.args):
                    parent.args.pop(parent_arg_index)

    def level_order_traversal(self):
        current_level = deque([self])
        next_level = deque()
        while current_level:
            level_nodes = []
            while current_level:
                node = current_level.popleft()
                level_nodes.append(node.origin)
                if node.args:
                    for arg in node.args:
                        if isinstance(arg, TypeVarModel):
                            next_level.append(arg)
                        elif isinstance(arg, list):
                            for a in arg:
                                if isinstance(a, TypeVarModel):
                                    next_level.append(a)
            yield level_nodes
            current_level, next_level = next_level, deque()

    def get_max_depth(self):
        max_depth = 0

        def dfs(node, depth):
            nonlocal max_depth
            if isinstance(node, TypeVarModel):
                max_depth = max(max_depth, depth)
                if node.args:
                    for arg in node.args:
                        if isinstance(arg, TypeVarModel):
                            dfs(arg, depth + 1)
                        elif isinstance(arg, list):
                            for a in arg:
                                if isinstance(a, TypeVarModel):
                                    dfs(a, depth + 1)

        dfs(self, 1)
        return max_depth

    def __str__(self):
        return f"{self.__class__.__name__}({self.get_instance()})"


def gen_typevar_model(invar: Type[In]):
    origin = get_real_origin(invar)
    args = get_args(invar)
    if origin is None and args == ():
        return TypeVarModel(origin=invar)
    elif origin is Optional:
        origin = Union
    args_list = []
    for arg in args:
        if isinstance(arg, list):
            args_list.append([gen_typevar_model(a) for a in arg])
        else:
            args_list.append(gen_typevar_model(arg))
    obj = TypeVarModel(origin=origin, args=args_list or None)
    return obj


def iter_deep_type(invar: Type[In]):
    obj = gen_typevar_model(invar)
    max_depth = obj.get_max_depth()
    yield obj.get_instance()
    for _ in reversed(range(1, max_depth)):
        obj.remove_deepest_level_node()
        yield obj.get_instance()


def infer_generic_type(type_var: Type[Any], instance: dict[Type[TypeVar], Type]):
    model = gen_typevar_model(type_var)
    return model.get_instance(instance)


def extract_typevar_mapping(
    template: TypeVarModel | Type | Any,
    instance: TypeVarModel | Type | Any,
) -> dict[Type[TypeVar], Type]:
    """Extracts type variable mappings from the template and instance TypeVarModel."""
    typevar_mapping = {}

    if not isinstance(template, TypeVarModel):
        template = gen_typevar_model(template)
    if not isinstance(instance, TypeVarModel):
        instance = gen_typevar_model(instance)

    def traverse(template_node: TypeVarModel, instance_node: TypeVarModel):
        if is_typevar(template_node.origin):
            typevar_mapping[template_node.origin] = instance_node.get_instance()
        elif like_issubclass(instance_node.origin, template_node.origin):
            if template_node.args and instance_node.args:
                if len(template_node.args) != len(instance_node.args):
                    raise ValueError(
                        "Template and instance have a different number of arguments"
                    )
                for tmpl_arg, inst_arg in zip(template_node.args, instance_node.args):
                    if isinstance(tmpl_arg, TypeVarModel) and isinstance(
                        inst_arg, TypeVarModel
                    ):
                        traverse(tmpl_arg, inst_arg)
                    elif isinstance(tmpl_arg, list) and isinstance(inst_arg, list):
                        for t_arg, i_arg in zip(tmpl_arg, inst_arg):
                            if isinstance(t_arg, TypeVarModel) and isinstance(
                                i_arg, TypeVarModel
                            ):
                                traverse(t_arg, i_arg)
                    else:
                        raise ValueError(
                            "Mismatch in structure between template and instance"
                        )
        else:
            raise ValueError(
                f"Instance node doesn't match the expected type: {template_node.origin} vs {instance_node.origin}"
            )

    traverse(template, instance)
    return typevar_mapping


def check_typevar_model(
    instance: TypeVarModel | Type | Any, template: TypeVarModel | Type | Any
) -> bool:
    if not isinstance(template, TypeVarModel):
        template = gen_typevar_model(template)
    if not isinstance(instance, TypeVarModel):
        instance = gen_typevar_model(instance)

    if template.origin in (types.UnionType, Union) and instance.origin in (
        types.UnionType,
        Union,
    ):
        return all(
            check_typevar_model(i_sub_arg, template)
            for i_sub_arg in instance.args  # type: ignore
        )
    if template.origin in (Union, types.UnionType):
        return any(
            check_typevar_model(instance, t_sub_arg)
            for t_sub_arg in template.args  # type: ignore
        )
    if instance.origin in (Union, types.UnionType):
        return all(
            check_typevar_model(i_sub_arg, template)
            for i_sub_arg in instance.args  # type: ignore
        )

    if is_generic_protocol_type(template.origin):
        ex_mapping = get_generic_mapping(template.get_instance())
        if is_generic_type(instance.get_instance()):
            tp_mapping = get_generic_mapping(instance.get_instance())
            return like_issubclass(
                instance.origin, template.origin, tp_mapping, ex_mapping
            )

        return like_issubclass(instance.origin, template.origin, ex_mapping=ex_mapping)
    elif is_typevar(template.origin):
        bound = get_bound(template.origin)
        if bound is not None:
            if not check_typevar_model(instance.origin, bound):
                return False
        constraints = get_constraints(template.origin)
        if constraints:
            if not any(check_typevar_model(instance.origin, c) for c in constraints):
                return False
        return True

    if not like_issubclass(instance.origin, template.origin):
        return False
    if template.args is None and instance.args is None:
        return True
    if template.args is not None and instance.args is None:
        return False
    if template.args is None and instance.args is not None:
        return True
    if len(template.args) != len(instance.args):  # type: ignore
        return False

    for i_arg, t_arg in zip(instance.args, template.args):  # type: ignore
        if isinstance(t_arg, TypeVarModel) and isinstance(i_arg, TypeVarModel):
            if not check_typevar_model(i_arg, t_arg):
                return False
        elif isinstance(t_arg, list) and isinstance(i_arg, list):
            for i_sub_arg, t_sub_arg in zip(i_arg, t_arg):
                if isinstance(t_sub_arg, TypeVarModel) and isinstance(
                    i_sub_arg, TypeVarModel
                ):
                    if not check_typevar_model(i_sub_arg, t_sub_arg):
                        return False
                else:
                    return False
        else:
            return False
    return True
