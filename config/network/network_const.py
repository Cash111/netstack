# -*- coding: utf-8 -*-
# @Time : 2022/7/6 22:23
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : network_const.py
# @Description: None
class IPv4Const:
    IPV4_MINIMUM_SIZE = 20

    IPV4_MAXIMUM_HEADER_SIZE = 60

    IPV4_ADDRESS_SIZE = 4

    IPV4_PROTOCOL_NUMBER = 0x0800

    IPV4_VERSION = 4

    IPV4_BROAD_CAST = b"\xff\xff\xff\xff"

    IPV4_ANY = b"\x00\x00\x00\x00"


class IPv6Const:
    IPV6_MINIMUM_SIZE = 40

    IPV6_ADDRESS_SIZE = 16

    IPV6_PROTOCOL_NUMBER = 0x86DD

    IPV6_VERSION = 6

    IPV6_MINIMUM_MTU = 1280


class ARPConst:
    PROTOCOL_NAME = "arp"

    PROTOCOL_ADDRESS = "arp"

    PROTOCOL_NUMBER = 0x0806

    ARP_SIZE = 2 + 2 + 1 + 1 + 2 + 2 * 6 + 2 * 4

    ARP_REQUEST = 1

    ARP_REPLY = 2

    RARP_REQUEST = 3

    RARP_REPLY = 4

    BROADCAST_MAC = bytearray([0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
