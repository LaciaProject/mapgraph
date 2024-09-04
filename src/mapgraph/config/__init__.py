import json
import os
from typing import Iterable, Mapping, Optional

from dotenv import dotenv_values
from typing_inspect import is_new_type

from ..globals import GLOBAL_INSTANCE_CONTEXT


def witch_type(value: str, _type):
    if issubclass(_type, str):
        return value
    elif issubclass(_type, bool):
        if value in ["True", "true", "1"]:
            return True
        elif value in ["False", "false", "0"]:
            return False
        return bool(value)
    elif issubclass(_type, float):
        return float(value)
    elif issubclass(_type, int):
        return int(value)
    elif issubclass(_type, dict):
        return json.loads(value)
    elif issubclass(_type, list):
        return json.loads(value)
    return value


def load_env(
    envs: Iterable,
    envs_kv: Optional[Mapping] = None,
    dotenv_path: Optional[str] = None,
    os_environ: bool = True,
):
    if os_environ and dotenv_path:
        env = {**dict(os.environ), **dotenv_values(dotenv_path=dotenv_path)}
    elif dotenv_path:
        env = dotenv_values(dotenv_path=dotenv_path)
    elif os_environ:
        env = dict(os.environ)
    else:
        env = {}
    if envs_kv:
        for e, v in envs_kv.items():
            value = env.get(e.__name__, None) or v
            if value is None:
                continue
            if is_new_type(e):
                GLOBAL_INSTANCE_CONTEXT.store(
                    {e: e(witch_type(value, e.__supertype__))}
                )
            else:
                GLOBAL_INSTANCE_CONTEXT.store({e: value})

    for e in envs:
        name = e.__name__
        if name in env:
            value = env[name]
            if value is None:
                continue
            if is_new_type(e):
                GLOBAL_INSTANCE_CONTEXT.store(
                    {e: e(witch_type(value, e.__supertype__))}
                )
            else:
                GLOBAL_INSTANCE_CONTEXT.store({e: value})
