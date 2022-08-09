# -*- coding: utf-8 -*-
# @Time : 2022/7/1 14:26
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : route.py
# @Description: None
from stack.nic import ReferencedNetworkEndpoint
from protocol.tcpip import Stats


class Router(object):
    def __init__(
        self,
        remote_address: str = "",
        remote_link_address: bytearray = None,
        local_address: str = "",
        local_link_address: bytearray = None,
        next_hop: str = "",
        network_protocol_number: int = -1,
        referenced_network_endpoint: ReferencedNetworkEndpoint = None,
    ):
        self.remote_address = remote_address
        self.remote_link_address = remote_link_address
        self.local_address = local_address
        self.local_link_address = local_link_address
        self.next_hop = next_hop
        self.network_protocol_number = network_protocol_number
        self.referenced_network_endpoint = referenced_network_endpoint

    def stats(self) -> Stats:
        return self.referenced_network_endpoint.nic.stack.stats
