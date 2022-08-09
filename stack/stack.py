# -*- coding: utf-8 -*-
# @Time : 2022/7/1 17:45
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : stack.py
# @Description: None
from typing import Dict, List, Callable, Optional
from threading import Lock
from config.stack.stack_const import NICConst
from stack.nic import NIC
from protocol.tcpip import Stats, Route, Clock
from stack.registration import (
    TransportProtocol,
    NetworkProtocol,
    LinkAddressResolver,
    TransportEndpointID,
)
from stack.route import Router
from stack.transport_demuxer import TransportDeMuxer
from stack.link_addr_cache import LinkAddrCache


class TransportProtocolState(object):
    def __init__(
        self,
        protocol: TransportProtocol,
        default_handler: Callable[[Router, TransportEndpointID, bytes], bool],
    ):
        self.protocol = protocol
        self.default_handler = default_handler


class Stack(object):
    def __init__(
        self,
        transport_protocols: Dict[int, TransportProtocolState],
        network_protocols: Dict[int, NetworkProtocol],
        link_addr_resolvers: Dict[int, LinkAddressResolver],
        de_muxer: TransportDeMuxer,
        stats: Stats,
        link_addr_cache: LinkAddrCache,
        lock: Lock,
        nics: Dict[int, NIC],
        forwarding: bool,
        route_table: List[Route],
        port_manager,
        tcp_probe_func: Callable,
        clock: Clock,
    ):
        self.transport_protocols = transport_protocols
        self.network_protocols = network_protocols
        self.link_addr_resolvers = link_addr_resolvers
        self.de_muxer = de_muxer
        self.stats = stats
        self.link_addr_cache = link_addr_cache
        self.lock = lock
        self.nics = nics
        self.forwarding = forwarding
        self.route_table = route_table
        self.port_manager = port_manager
        self.tcp_probe_func = tcp_probe_func
        self.clock = clock

    def find_router(
        self,
        nic_id: int,
        local_address: str,
        remote_address: str,
        network_protocol_number: int,
    ) -> Router or None:
        """

        :param nic_id:
        :param local_address:
        :param remote_address:
        :param network_protocol_number:
        :return:
        """
        for route in self.route_table:
            if (nic_id != 0 and nic_id != route.nic_id) or (
                len(remote_address) != 0 and not route.match(local_address)
            ):
                continue
            nic: NIC = self.nics.get(route.nic_id)
            if not nic:
                continue
            if len(local_address) != 0:
                ref = nic.find_endpoint(
                    network_protocol_number=network_protocol_number,
                    address=local_address,
                    primary_endpoint_behavior=NICConst.CAN_BE_PRIMARY_ENDPOINT,
                )
            else:
                ref = nic.primary_endpoint(protocol_number=network_protocol_number)
            if not ref:
                continue

            if len(remote_address) == 0:
                remote_address = ref.ep.id.local_address

            _route = Router(
                network_protocol_number=network_protocol_number,
                local_address=ref.ep.id.local_address,
                remote_address=remote_address,
                local_link_address=nic.link_ep.link_address,
                referenced_network_endpoint=ref,
            )
            _route.next_hop = route.gateway
            return _route
        return None
