# -*- coding: utf-8 -*-
# @Time : 2022/6/30 22:05
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : registration.py
# @Description: None
import abc
from libs.typing import *

from libs.logger import logger


class NetworkEndpointID(object):
    def __init__(self, address):
        self.local_address = address


class TransportEndpointID(object):
    def __init__(
        self,
        local_port: int = 0,
        local_address: str = "",
        remote_port: int = 0,
        remote_address: str = "",
    ):
        self.local_port = local_port
        self.local_address = local_address
        self.remote_port = remote_port
        self.remote_address = remote_address


class LinkEndpoint(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def mtu(self) -> int:
        """
        :return:
        """

    @property
    @abc.abstractmethod
    def capabilities(self) -> int:
        """
        :return:
        """

    @property
    @abc.abstractmethod
    def max_header_length(self) -> int:
        """
        :return:
        """

    @property
    @abc.abstractmethod
    def link_address(self) -> bytearray:
        """
        :return:
        """

    @abc.abstractmethod
    def write_packet(self, router, header, payload, protocol):
        """
        :param router:
        :param header:
        :param payload:
        :param protocol:
        :return:
        """

    @abc.abstractmethod
    def attach(self, dispatcher):
        """
        :param dispatcher:
        :return:
        """

    @property
    @abc.abstractmethod
    def is_attach(self) -> bool:
        """

        :return:
        """


class NetworkDispatcher(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def deliver_network_packet(
        self,
        link_ep: LinkEndpoint,
        dst_link_addr: bytearray,
        src_link_addr: bytearray,
        protocol: int,
        buffer: bytearray,
    ):
        """
        :param link_ep:
        :param dst_link_addr:
        :param src_link_addr:
        :param protocol:
        :param buffer:
        :return:
        """


class TransportDispatcher(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def deliver_transport_packet(self, route, transport_protocol_number, buffer):
        pass

    @abc.abstractmethod
    def deliver_transport_control_packet(
        self,
        local_addr,
        remote_addr,
        network_protocol_number,
        transport_protocol_number,
        control_type: int,
        extra: int,
        buffer: list,
    ):
        """

        :param local_addr:
        :param remote_addr:
        :param network_protocol_number:
        :param transport_protocol_number:
        :param control_type:
        :param extra:
        :param buffer:
        :return:
        """


class NetworkEndpoint(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def default_ttl(self) -> int:
        """

        :return:
        """

    @property
    @abc.abstractmethod
    def mtu(self) -> int:
        """

        :return:
        """

    @property
    @abc.abstractmethod
    def capabilities(self) -> int:
        """

        :return:
        """

    @property
    @abc.abstractmethod
    def max_header_length(self) -> int:
        """
        :return:
        """

    @property
    @abc.abstractmethod
    def id(self) -> NetworkEndpointID:
        """

        :return:
        """

    @property
    @abc.abstractmethod
    def nic_id(self) -> int:
        """

        :return:
        """

    @abc.abstractmethod
    def write_packet(self, route, header, payload, protocol, ttl: int):
        """
        :param ttl:
        :param route:
        :param header:
        :param payload:
        :param protocol:
        :return:
        """

    @abc.abstractmethod
    def handle_packet(self, router, buffer):
        """

        :param router:
        :param buffer:
        :return:
        """

    @abc.abstractmethod
    def close(self):
        """

        :return:
        """


class NetworkProtocol(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def number(self) -> int:
        """
        return protocol number
        :return:
        """

    @property
    @abc.abstractmethod
    def minimum_packet_size(self) -> int:
        """

        :return:
        """

    @abc.abstractmethod
    def parse_addresses(self, buffer: bytes) -> (str, str):
        """
        :param buffer:
        :return:
        """

    @abc.abstractmethod
    def new_endpoint(
        self,
        nic_id: NIC_ID,
        addr: str,
        link_addr_cache,
        dispatcher: NetworkDispatcher,
        sender: LinkEndpoint,
    ) -> NetworkEndpoint:
        """
        :param nic_id:
        :param addr:
        :param link_addr_cache:
        :param dispatcher:
        :param sender:
        :return:
        """

    @abc.abstractmethod
    def set_option(self, opt):
        """
        :param opt:
        :return:
        """

    @abc.abstractmethod
    def option(self, opt):
        """

        :return:
        """


class TransportEndpoint(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def handle_packet(self, router, transport_endpoint_id: TransportEndpointID, buffer: bytes):
        """

        :param transport_endpoint_id:
        :param router:
        :param buffer:
        :return:
        """

    @abc.abstractmethod
    def handle_control_packet(
        self,
        transport_id: TransportEndpointID,
        control_type: int,
        extra: int,
        buffer: list,
    ):
        """

        :param transport_id:
        :param control_type:
        :param extra:
        :param buffer:
        :return:
        """


class TransportProtocol(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def number(self) -> int:
        """
        return protocol number
        :return:
        """

    @property
    @abc.abstractmethod
    def minimum_packet_size(self) -> int:
        """

        :return:
        """

    @abc.abstractmethod
    def parse_ports(self, buffer: bytes) -> (int, int):
        """
        :param buffer:
        :return:
        """

    @abc.abstractmethod
    def new_endpoint(self, stack, network_protocol_number, wait_queue):
        """
        :param stack:
        :param network_protocol_number:
        :param wait_queue:
        :return: tcpip.Endpoint
        """

    @abc.abstractmethod
    def set_option(self, opt):
        """
        :param opt:
        :return:
        """

    @abc.abstractmethod
    def option(self, opt):
        """

        :return:
        """

    @abc.abstractmethod
    def handle_unknown_destination_packet(
        self, router, transport_endpoint_id, buffer
    ) -> bool:
        """

        :param router:
        :param transport_endpoint_id:
        :param buffer:
        :return:
        """


class LinkAddressCache(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def check_local_address(self, nic_id: NIC_ID, protocol_number: PROTOCOL_NUMBER, address: ADDRESS) -> NIC_ID:
        """
        :param nic_id:
        :param protocol_number:
        :param address:
        :return:
        """

    @abc.abstractmethod
    def add_link_address(self, nic_id: NIC_ID, address: ADDRESS, link_address: LINK_ADDRESS):
        """

        :param nic_id:
        :param address:
        :param link_address:
        :return:
        """

    @abc.abstractmethod
    def get_link_address(self, nic_id: NIC_ID, address: ADDRESS, local_address: ADDRESS, protocol_number: PROTOCOL_NUMBER):
        """

        :param nic_id:
        :param address:
        :param local_address:
        :param protocol_number:
        :return:
        """


class LinkAddressResolver(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def link_address_request(
        self, address: bytes, local_address: bytes, link_ep: LinkEndpoint
    ):
        """
        :return:
        """

    @abc.abstractmethod
    def resolve_static_address(self, address: str) -> str:
        """

        :param address:
        :return:
        """

    @property
    @abc.abstractmethod
    def link_address_protocol(self) -> int:
        """

        :return:
        """


TransportProtocols: Dict[str, Callable[[], TransportProtocol]] = {}
NetworkProtocols: Dict[str, Callable[[], NetworkProtocol]] = {}
NextLinkEndpointID: int = 1
LinkEndpoints: Dict[id, LinkEndpoint] = {}


def register_link_endpoint(link_ep: LinkEndpoint) -> int:
    global NextLinkEndpointID, LinkEndpoints

    v = NextLinkEndpointID
    NextLinkEndpointID += 1
    LinkEndpoints[v] = link_ep
    logger.info("@stack: Registered link layer devices, id: {}".format(v))
    return v


if __name__ == "__main__":

    class B(LinkEndpoint):
        pass

    print(B().mtu)
