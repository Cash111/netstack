# -*- coding: utf-8 -*-
# @Time : 2022/7/4 11:32
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : stack_const.py
# @Description: None
class StackConst(object):
    CAPABILITY_CHECKSUM_OFFLOAD = 1
    CAPABILITY_RESOLUTION_REQUIRED = 2
    CAPABILITY_SAVE_RESTORE = 4
    CAPABILITY_DISCONNECT_OK = 8
    CAPABILITY_LOOPBACK = 16


class NICConst(object):
    CAN_BE_PRIMARY_ENDPOINT = 0
    FIRST_PRIMARY_ENDPOINT = 1
    NEVER_PRIMARY_ENDPOINT = 2
