# -*- coding: utf-8 -*-
# @Time : 2022/7/6 23:07
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : arp.py
# @Description: None
from typing import Optional
from libs.logger import logger
from protocol import errors
from protocol.header.arp import ARP
from config.link.link_const import LinkConst
from config.network.network_const import ARPConst, IPv4Const
from stack.route import Router
from stack.registration import LinkEndpoint, NetworkDispatcher
from stack.registration import (
    NetworkEndpoint,
    NetworkEndpointID,
    NetworkProtocol,
    LinkAddressResolver,
)
from stack.link_address_cache import LinkAddressCache


class ARPEndpoint(NetworkEndpoint):
    def __init__(
        self,
        nic_id: int,
        address: str,
        link_ep: LinkEndpoint,
        link_address_cache: LinkAddressCache,
    ):
        self._nic_id = nic_id
        self.address = address
        self.link_ep = link_ep
        self.link_address_cache = link_address_cache

    @property
    def default_ttl(self) -> int:
        return 0

    @property
    def mtu(self) -> int:
        link_mtu = self.link_ep.mtu
        return link_mtu

    @property
    def capabilities(self) -> int:
        return self.link_ep.capabilities

    @property
    def max_header_length(self) -> int:
        return self.link_ep.max_header_length + ARPConst.ARP_SIZE

    @property
    def id(self) -> NetworkEndpointID:
        return NetworkEndpointID(address=ARPConst.PROTOCOL_ADDRESS)

    @property
    def nic_id(self) -> int:
        return self._nic_id

    def write_packet(self, route, header, payload, protocol, ttl: int):
        raise errors.NotSupportError("operation not supported")

    def handle_packet(self, router, buffer: bytearray):
        logger.info(
            "@network: Resolves ARP packets, including ARP requests and replies."
        )
        arp_pkt = ARP(buffer)
        if not arp_pkt.is_valid():
            return

        if arp_pkt.op() == ARPConst.ARP_REQUEST:
            logger.info("@network: Resolves ARP request packets.")
            local_address = str(arp_pkt.protocol_address_target())
            if (
                self.link_address_cache.check_local_address(
                    self.nic_id, router.network_protocol_number, local_address
                )
                == 0
            ):
                return
            header_pkt = ARP(ARPConst.ARP_SIZE)
            header_pkt.set_ipv4_over_ethernet()
            header_pkt.set_op(ARPConst.ARP_REPLY)
            header_pkt.hardware_address_sender(router.local_link_address)
            header_pkt.hardware_address_target(arp_pkt.hardware_address_sender())
            header_pkt.protocol_address_sender(arp_pkt.protocol_address_target())
            header_pkt.protocol_address_target(arp_pkt.protocol_address_sender())
            logger.info(
                "@network: arp reply: {}, {}".format(
                    arp_pkt.protocol_address_sender(), arp_pkt.hardware_address_target()
                )
            )
            self.link_ep.write_packet(
                router=router,
                header=header_pkt,
                payload=buffer,
                protocol=ARPConst.PROTOCOL_NUMBER,
            )
            self._resolve_arp_reply(arp_packet=arp_pkt)
        elif arp_pkt.op() == ARPConst.ARP_REPLY:
            self._resolve_arp_reply(arp_packet=arp_pkt)

    def _resolve_arp_reply(self, arp_packet: ARP):
        """
        Resolves ARP reply packets.
        :param arp_packet:
        :return:
        """
        logger.info("@network: Resolves ARP reply packets.")
        address = str(arp_packet.protocol_address_sender())
        link_address = arp_packet.hardware_address_sender()
        self.link_address_cache.add_link_address(self.nic_id, address, link_address)

    def close(self):
        pass


class ARPProtocol(NetworkProtocol, LinkAddressResolver):
    @property
    def number(self) -> int:
        return ARPConst.PROTOCOL_NUMBER

    @property
    def minimum_packet_size(self) -> int:
        return ARPConst.ARP_SIZE

    def parse_addresses(self, buffer: bytes) -> (str, str):
        arp_buffer = ARP(buffer)
        return str(arp_buffer.protocol_address_sender()), ARPConst.PROTOCOL_ADDRESS

    def new_endpoint(
        self,
        nic_id: int,
        addr: str,
        link_addr_cache: LinkAddressCache,
        dispatcher: NetworkDispatcher,
        sender: LinkEndpoint,
    ) -> Optional[NetworkEndpoint]:
        if addr != ARPConst.PROTOCOL_ADDRESS:
            return None
        return ARPEndpoint(
            nic_id=nic_id,
            address=addr,
            link_ep=sender,
            link_address_cache=link_addr_cache,
        )

    def set_option(self, opt):
        raise errors.UnknownProtocolOptionError("unknown option for protocol")

    def option(self, opt):
        raise errors.UnknownProtocolOptionError("unknown option for protocol")

    def link_address_request(
        self, address: bytes, local_address: bytes, link_ep: LinkEndpoint
    ):
        router = Router(remote_link_address=ARPConst.BROADCAST_MAC)
        buffer = bytearray(LinkConst.ETH_MIN_SIZE + ARPConst.ARP_SIZE)
        arp_buffer = ARP(buffer)
        arp_buffer.set_ipv4_over_ethernet()
        arp_buffer.set_op(ARPConst.ARP_REQUEST)
        arp_buffer.hardware_address_sender(link_ep.link_address)
        arp_buffer.protocol_address_sender(bytearray(local_address))
        arp_buffer.protocol_address_target(bytearray(address))
        return link_ep.write_packet(router=router, header=buffer, payload=arp_buffer, protocol=ARPConst.PROTOCOL_NUMBER)

    def resolve_static_address(self, address: bytes) -> Optional[bytearray]:
        if address == b"\xff\xff\xff\xff":
            return ARPConst.BROADCAST_MAC
        return None

    @property
    def link_address_protocol(self) -> int:
        return IPv4Const.IPV4_PROTOCOL_NUMBER
