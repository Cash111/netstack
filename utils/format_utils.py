# -*- coding: utf-8 -*-
# @Time : 2022/6/30 21:50
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : format_utils.py
# @Description: None

class FormatUtils(object):
    @staticmethod
    def format_hex(hex_list: list):
        for num in hex_list:
            yield "%02x" % num

    @staticmethod
    def hex_to_int(hex_bytes):
        return int.from_bytes(hex_bytes, byteorder="big", signed=False)
