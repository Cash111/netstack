# -*- coding: utf-8 -*-
# @Time : 2022/7/8 18:09
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : arp.py
# @Description: None
import IPy

from libs.logger import logger
from config.network.network_const import IPv4Const, IPv6Const
from config.link.link_const import LinkConst
from protocol.link.tuntap.tuntap import TunTap
from stack.stack import Stack
from stack.link_address_cache import LinkAddressCache
from protocol.link.fdbased.endpoint import Endpoint, Options


def main(tap_name, cidr_name):
    ip = IPy.IP(cidr_name)
    if ip.version() == IPv4Const.IPV4_VERSION:
        addr = ip.strNormal()
        protocol = IPv4Const.IPV4_PROTOCOL_NUMBER
    elif ip.version() == IPv6Const.IPV6_VERSION:
        addr = ip.strNormal()
        protocol = IPv6Const.IPV6_PROTOCOL_NUMBER
    else:
        logger.error("Unknown ip type: {}".format(cidr_name))
        return
    fd = TunTap.new_net_dev(name=tap_name, mode=LinkConst.TAP)
    if fd < 0:
        raise

    TunTap.set_link_up(tap_name)
    TunTap.set_route(tap_name, cidr_name)
    mac = TunTap.get_hardware_addr(tap_name)
    logger.info("get mac addr: {}".format(mac))

    options = Options(
        fd=fd,
        mtu=1500,
        link_address=mac
    )

    stack = Stack(
        transport_protocols={},
        network_protocols={},
        link_addr_resolvers={},
        nics={},
        link_addr_cache=LinkAddressCache
    )
