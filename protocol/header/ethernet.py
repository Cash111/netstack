# -*- coding: utf-8 -*-
# @Time : 2022/6/30 15:37
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : ethernet.py
# @Description: None
from typing import List

from config.link.link_const import LinkConst


class Ethernet(object):
    def __init__(self, dst_addr: bytearray = None, src_addr: bytearray = None, eth_type: bytearray = None):
        self.dst_addr = dst_addr
        self.src_addr = src_addr
        self.type = eth_type

    def from_bytes(self, eth_data: bytearray):
        assert len(eth_data) > LinkConst.ETH_MIN_SIZE
        self.dst_addr = eth_data[LinkConst.DST_MAC_OFFSET:][:LinkConst.ETH_ADDR_SIZE]
        self.src_addr = eth_data[LinkConst.SRC_MAC_OFFSET:][:LinkConst.ETH_ADDR_SIZE]
        self.type = eth_data[LinkConst.ETH_Type_OFFSET:][:LinkConst.ETH_TYPE_SIZE]
        return self

    def encode(self) -> bytearray:
        assert len(self.dst_addr) == LinkConst.ETH_ADDR_SIZE and len(self.src_addr) == LinkConst.ETH_ADDR_SIZE
        buff = bytearray()
        buff.extend(self.dst_addr)
        buff.extend(self.src_addr)
        buff.extend(self.type)
        return buff

    @staticmethod
    def trim_front(buf: bytearray, count: int):
        return buf[count:]


if __name__ == '__main__':
    from utils.format_utils import FormatUtils
    # a = b'33\x00\x00\x00\x16\xba(\xfd\xf9\x81d\x86\xdd`\x00\x00\x00\x00$\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x16:\x00\x05\x02\x00\x00\x01\x00\x8f\x00\xed,\x00\x00\x00\x01\x04\x00\x00\x00\xff\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xff\xf9\x81d'
    # Ethernet.decode(a)
    # print(":".join([h for h in FormatUtils.format_hex(Ethernet.dst_addr)]))
    # print(":".join([h for h in FormatUtils.format_hex(Ethernet.src_addr)]))
    # print(":".join([h for h in FormatUtils.format_hex(Ethernet.type)]))
    # print(":".join([h for h in FormatUtils.format_hex(Ethernet.encode())]))
    # print(Ethernet.src_addr)
    e = Ethernet(dst_addr=[186, 40, 253, 249, 129, 100], src_addr=[186, 40, 253, 249, 129, 100], eth_type=[134, 221])
    print(e.src_addr)
    # print(e.encode())
