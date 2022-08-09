# -*- coding: utf-8 -*-
# @Time : 2022/6/30 15:54
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : const.py
# @Description: None

class LinkConst:
    TUN = 1
    TAP = 2
    IFNAMSIZ = 16

    DST_MAC_OFFSET = 0
    SRC_MAC_OFFSET = 6
    ETH_Type_OFFSET = 12

    ETH_MIN_SIZE = 14
    ETH_ADDR_SIZE = 6
    ETH_TYPE_SIZE = 2

    DEFAULT_READ_SIZE = 1024

    MIN_EHTER_PKG_LEN = 46

    BUF_CONFIG = [128, 256, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]


class SysCall:
    IFF_TUN = 0x1
    IFF_TAP = 0x2
    IFF_NO_PI = 0x1000
    TUNSETIFF = 0x400454CA
    SIOCGIFHWADDR = 0x8927
    SIOCSIFMTU = 0x8922
