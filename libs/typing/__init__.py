# -*- coding: utf-8 -*-
# @Time : 2022/8/1 18:28
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : __init__.py.py
# @Description: None
__all__ = [
    "NIC_ID",
    "LINK_ADDRESS",
    "ADDRESS",
    "PROTOCOL_NUMBER",
    "T",
    "Callable",
    "Mapping",
    "List",
    "Iterator",
    "Dict",
    "STATE",
    "TIMESTAMP",
]

from typing import *

NIC_ID = NewType("NIC_ID", int)
LINK_ADDRESS = NewType("LINK_ADDRESS", bytes)
ADDRESS = NewType("ADDRESS", bytes)
PROTOCOL_NUMBER = NewType("PROTOCOL_NUMBER", int)
TIMESTAMP = NewType("TIMESTAMP", int)
STATE = NewType("STATE", int)
T = TypeVar("T")
