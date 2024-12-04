import json
import os
from typing import Iterable, Mapping, Optional

import yaml
from pydantic import BaseModel
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
        return json.loads(value) if isinstance(value, str) else value
    elif issubclass(_type, list):
        return json.loads(value) if isinstance(value, str) else value
    return value


def load_env(
    envs: Iterable,
    envs_kv: Optional[Mapping] = None,
    dotenv_path: Optional[str] = None,
    yaml_path: Optional[str] = None,
    os_environ: bool = True,
):
    env = {}
    if dotenv_path:
        env.update(dotenv_values(dotenv_path=dotenv_path))
    elif yaml_path:
        with open(yaml_path) as f:
            yaml_data = yaml.safe_load(f)
        env.update(yaml_data)
    elif os_environ:
        env.update(dict(os.environ))
    if envs_kv:
        for e, v in envs_kv.items():
            value = env.get(e.__name__, None) or v
            if value is None:
                continue
            if is_new_type(e):
                GLOBAL_INSTANCE_CONTEXT.store(
                    {e: e(witch_type(value, e.__supertype__))}
                )
            elif issubclass(e, BaseModel):
                GLOBAL_INSTANCE_CONTEXT.store({e: e(**value)})
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
            elif issubclass(e, BaseModel):
                GLOBAL_INSTANCE_CONTEXT.store({e: e(**value)})
            else:
                GLOBAL_INSTANCE_CONTEXT.store({e: value})
