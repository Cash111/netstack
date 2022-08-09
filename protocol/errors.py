# -*- coding: utf-8 -*-
# @Time : 2022/6/30 15:59
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : errors.py
# @Description: None
class CommandError(Exception):
    pass


class DuplicateAddressError(Exception):
    pass


class BadLocalAddressError(Exception):
    pass


class NotSupportError(Exception):
    pass


class UnknownProtocolOptionError(Exception):
    pass
