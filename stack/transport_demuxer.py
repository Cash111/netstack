# -*- coding: utf-8 -*-
# @Time : 2022/7/1 17:49
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : transport_demuxer.py
# @Description: None
import typing

from stack.registration import TransportEndpoint, TransportEndpointID
from stack.route import Router
from config.header.header_const import UDPConst


class TransportEndpoints(object):
    def __init__(self, endpoints: typing.Dict[TransportEndpointID, TransportEndpoint]):
        self.endpoints = endpoints


class ProtocolIDs(object):
    def __init__(
        self, network_protocol_number: int = 0, transport_protocol_number: int = 0
    ):
        self.network_protocol_number = network_protocol_number
        self.transport_protocol_number = transport_protocol_number


class TransportDeMuxer(object):
    def __init__(self, protocol: typing.Dict[ProtocolIDs, TransportEndpoints]):
        self.protocol = protocol

    def deliver_packet(
        self,
        router: Router,
        transport_protocol_number: int,
        buffer: bytes,
        transport_endpoint_id: TransportEndpointID,
    ) -> bool:
        """

        :param router:
        :param transport_protocol_number:
        :param buffer:
        :param transport_endpoint_id:
        :return:
        """
        eps = self.protocol.get(
            ProtocolIDs(
                network_protocol_number=router.network_protocol_number,
                transport_protocol_number=transport_protocol_number,
            )
        )
        if not eps:
            return False
        ep = self.find_endpoint(eps, buffer, transport_endpoint_id)
        if not ep:
            if transport_protocol_number == UDPConst.UDP_PROTOCOL_NUMBER:
                router.stats().udp.unknown_port_errors.increment()
                return False

        ep.handle_packet(router=router, transport_endpoint_id=transport_endpoint_id, buffer=buffer)
        return True

    def find_endpoint(
        self,
        eps: TransportEndpoints,
        buffer: bytes,
        transport_endpoint_id: TransportEndpointID,
    ) -> typing.Optional[TransportEndpoint]:
        ep = eps.endpoints.get(transport_endpoint_id)
        if ep:
            return ep

        nid = transport_endpoint_id
        nid.local_address = ""
        ep = eps.endpoints.get(nid)
        if ep:
            return ep

        nid.local_address = transport_endpoint_id.local_address
        nid.remote_address = ""
        nid.remote_port = 0
        ep = eps.endpoints.get(nid)
        if ep:
            return ep
        nid.local_address = ""
        return eps.endpoints.get(nid)
