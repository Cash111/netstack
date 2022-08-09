# -*- coding: utf-8 -*-
# @Time : 2022/7/6 17:17
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : arp.py
# @Description: None
from typing import Optional
from config.network.network_const import ARPConst
from config.network.network_const import IPv4Const


class ARP(bytearray):
    def hardware_address_space(self) -> int:
        return int(self[0]) << 8 | int(self[1])

    def protocol_address_space(self) -> int:
        return int(self[2]) << 8 | int(self[3])

    def hardware_address_size(self) -> int:
        return int(self[4])

    def protocol_address_size(self) -> int:
        return int(self[5])

    def op(self) -> int:
        return int(self[6]) << 8 | int(self[7])

    def set_op(self, op: int):
        self[6] = int(op >> 8)
        self[7] = int(op)

    def set_ipv4_over_ethernet(self):
        self[0], self[1] = 0, 1
        self[2], self[3] = 0x08, 0x00
        self[4] = 6
        self[5] = int(IPv4Const.IPV4_ADDRESS_SIZE)

    def hardware_address_sender(self, set_array: bytearray = None) -> Optional[bytearray]:
        link_address_offset = 8
        if set_array:
            self._set_value(link_address_offset, link_address_offset + 6, set_array)
            return
        return self[link_address_offset: link_address_offset + 6]

    def protocol_address_sender(self, set_array: bytearray = None) -> Optional[bytearray]:
        address_offset = 14
        if set_array:
            self._set_value(address_offset, address_offset + 4, set_array)
            return
        return self[address_offset: address_offset + 4]

    def hardware_address_target(self, set_array: bytearray = None) -> Optional[bytearray]:
        link_address_offset = 18
        if set_array:
            self._set_value(link_address_offset, link_address_offset + 6, set_array)
            return
        return self[link_address_offset: link_address_offset + 6]

    def protocol_address_target(self, set_array: bytearray = None) -> Optional[bytearray]:
        address_offset = 24
        if set_array:
            self._set_value(address_offset, address_offset + 4, set_array)
            return
        return self[address_offset: address_offset + 4]

    def _set_value(self, low_offset: int, high_offset: int, array: bytearray):
        self[low_offset:high_offset] = array

    def is_valid(self) -> bool:
        if len(self) < ARPConst.ARP_SIZE:
            return False

        # 判断是否以太网协议，检查协议号和地址长度是否正确
        ethernet_type = 1
        mac_size = 6
        return (
                self.hardware_address_space() == ethernet_type
                and self.protocol_address_space() == IPv4Const.IPV4_PROTOCOL_NUMBER
                and self.hardware_address_size() == mac_size
                and self.protocol_address_size() == IPv4Const.IPV4_ADDRESS_SIZE
        )
