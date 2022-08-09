# -*- coding: utf-8 -*-
# @Time : 2022/7/1 17:45
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : nic.py
# @Description: None

from threading import Lock
from typing import Dict, List, Optional
from libs.ilist.ilist import Entry, IList
from config.stack.stack_const import StackConst, NICConst
from config.network.network_const import IPv4Const, IPv6Const
from libs.logger import logger
from stack.stack import Stack, LinkAddrCache
from stack.route import Router
from stack.registration import (
    LinkEndpoint,
    NetworkEndpointID,
    NetworkEndpoint,
    NetworkProtocol,
    TransportEndpointID,
)
from stack.transport_demuxer import TransportDeMuxer
from protocol.tcpip import Subnet
from protocol.header.ethernet import Ethernet
from protocol import errors


class ReferencedNetworkEndpoint(Entry):
    def __init__(
        self,
        refs: int,
        ep: NetworkEndpoint,
        nic,
        network_protocol_number: int,
        holds_insert_ref: bool,
        link_addr_cache: LinkAddrCache = None,
    ):
        super(ReferencedNetworkEndpoint, self).__init__()
        self.refs = refs
        self.ep = ep
        self.nic = nic
        self.network_protocol_number = network_protocol_number
        self.link_addr_cache = link_addr_cache
        self.holds_insert_ref = holds_insert_ref

    def dec_ref(self):
        if self.refs == 1:
            self.nic.remove_endpoint(self)

    def inc_ref(self):
        self.refs += 1

    def try_inc_ref(self) -> bool:
        if self.refs == 0:
            return False
        return True


class NIC(object):
    def __init__(
        self,
        stack: Stack,
        nic_id: int,
        name: str,
        link_ep: LinkEndpoint,
        de_muxer: TransportDeMuxer,
        lock: Lock,
        spoofing: bool,
        promiscuous: bool,
        primary: Dict[int],
        endpoints: Dict[NetworkEndpointID],
        subnets: List[Subnet],
    ):
        self.stack = stack
        self.nic_id = nic_id
        self.name = name
        self.link_ep = link_ep
        self.de_muxer = de_muxer
        self.lock = lock
        self.spoofing = spoofing
        self.promiscuous = promiscuous
        self.primary = primary
        self.endpoints = endpoints
        self.subnets = subnets

    def attach_link_endpoint(self):
        self.link_ep.attach(self)

    def set_promiscuous_mode(self, enable: bool):
        self.promiscuous = enable

    def is_promiscuous_mode(self) -> bool:
        return self.promiscuous

    def set_spoofing(self, enable: bool):
        self.spoofing = enable

    def get_main_nic_address(self, protocol_number: int) -> (str, Subnet):
        if self.primary.get(protocol_number):
            # @TODO
            pass

    def primary_endpoint(self, protocol_number: int):
        pass

    def add_address_locked(
        self,
        protocol_number: int,
        address: str,
        primary_endpoint_behavior: int,
        replace: bool,
    ) -> Optional[ReferencedNetworkEndpoint]:
        logger.info(
            "@nic: register protocol to nic, protocol: {}, address: {}".format(
                protocol_number, address
            )
        )
        net_protocol = self.stack.network_protocols.get(protocol_number)
        if not net_protocol:
            logger.warning("@nic: protocol {} is not supported".format(protocol_number))
            return None
        endpoint = net_protocol.new_endpoint(
            nic_id=self.nic_id,
            addr=address,
            link_addr_cache=self.stack,
            dispatcher=self,
            sender=self.link_ep,
        )
        endpoint_id = endpoint.id
        ref = self.endpoints.get(endpoint_id)
        if not ref:
            if not replace:
                raise errors.DuplicateAddressError("duplicate address")
            else:
                self.remove_endpoint(ref)
        ref = ReferencedNetworkEndpoint(
            refs=1,
            ep=endpoint,
            nic=self,
            network_protocol_number=protocol_number,
            holds_insert_ref=True,
        )
        if self.link_ep.capabilities & StackConst.CAPABILITY_RESOLUTION_REQUIRED != 0:
            if self.stack.link_addr_resolvers.get(protocol_number):
                ref.link_addr_cache = self.stack

        self.endpoints[endpoint_id] = ref
        i_list: IList = self.primary.get(protocol_number)
        if not i_list:
            self.primary[protocol_number] = IList()
        if primary_endpoint_behavior == NICConst.CAN_BE_PRIMARY_ENDPOINT:
            i_list.append(ref)
        elif primary_endpoint_behavior == NICConst.FIRST_PRIMARY_ENDPOINT:
            i_list.add(ref)
        return ref

    def add_address(self, network_protocol_number: int, address: str):
        return self.add_address_with_options(
            network_protocol_number=network_protocol_number,
            address=address,
            primary_endpoint_behavior=NICConst.CAN_BE_PRIMARY_ENDPOINT,
        )

    def remove_address(self, address: str):
        r = self.endpoints[NetworkEndpointID(address)]
        if not r or not r.holds_insert_ref:
            raise errors.BadLocalAddressError("bad local address")
        r.holds_insert_ref = False
        r.decRef()
        return

    def find_endpoint(
        self, network_protocol_number: int, address: str, primary_endpoint_behavior: int
    ) -> Optional[ReferencedNetworkEndpoint]:
        network_endpoint_id = NetworkEndpointID(address)
        ref: Optional[ReferencedNetworkEndpoint] = self.endpoints.get(
            network_endpoint_id
        )
        if ref is not None and not ref.try_inc_ref():
            ref = None

        if ref is not None or not self.spoofing:
            return ref

        if ref is None or not ref.try_inc_ref():
            ref = self.add_address_locked(
                protocol_number=network_protocol_number,
                address=address,
                primary_endpoint_behavior=primary_endpoint_behavior,
                replace=True,
            )
            if ref is not None:
                ref.holds_insert_ref = False

        return ref

    def remove_endpoint(self, ref: ReferencedNetworkEndpoint):
        """
        :param ref:
        :return:
        """
        ip = ref.ep.id
        if self.endpoints[ip] != ref:
            return
        if ref.holds_insert_ref:
            raise Exception("Reference count dropped to zero before being removed")
        self.endpoints.pop(ip)
        was_in_list = (
            ref.next().value is not None
            or ref.prev().value is not None
            or ref == self.primary[ref.network_protocol_number].front()
        )
        if was_in_list:
            self.primary[ref.network_protocol_number].remove(ref)
        ref.ep.close()

    def add_address_with_options(
        self, network_protocol_number: int, address: str, primary_endpoint_behavior: int
    ):
        self.add_address_locked(
            protocol_number=network_protocol_number,
            address=address,
            primary_endpoint_behavior=primary_endpoint_behavior,
            replace=False,
        )

    def add_subnet(self, subnet: Subnet):
        self.subnets.append(subnet)

    def remove_subnet(self, subnet: Subnet):
        tmp_subnets = self.subnets
        tmp_subnets.remove(subnet)
        self.subnets = tmp_subnets

    def contains_subnet(self, subnet: Subnet) -> bool:
        return subnet in self.subnets

    def get_subnets(self) -> List[Subnet]:
        """
        :return:
        """
        subnets = []
        for nid in self.endpoints:
            subnet = Subnet.new_subnet(
                nid.local_address, list(b"\xff" * len(nid.local_address))
            )
            subnets.append(subnet)
        return subnets

    def deliver_network_packet(
        self,
        link_ep: LinkEndpoint,
        remote_link_addr: bytearray,
        local_link_addr: bytearray,
        network_protocol_number: int,
        buffer: bytearray,
    ):
        logger.info(
            "@nic: The nic parses the Ethernet protocol and distributes it to the corresponding network layer protocol for processing."
        )
        network_protocol: NetworkProtocol = self.stack.network_protocols.get(
            network_protocol_number
        )
        if not network_protocol:
            self.stack.stats.unknown_protocol_received_packets.increment()
            return
        if (
            network_protocol.number == IPv4Const.IPV4_PROTOCOL_NUMBER
            or network_protocol.number == IPv6Const
        ):
            self.stack.stats.ip.packets_received.increment()

        if len(buffer) < network_protocol.minimum_packet_size:
            self.stack.stats.malformed_received_packets.increment()
            return

        src, dst = network_protocol.parse_addresses(buffer)
        ref = self.get_ref(network_protocol_number=network_protocol_number, dst=dst)
        if ref:
            router = Router(
                remote_address=dst,
                remote_link_address=remote_link_addr,
                network_protocol_number=network_protocol_number,
                local_address=src,
                local_link_address=link_ep.link_address,
                referenced_network_endpoint=ref,
            )
            ref.ep.handle_packet(router, buffer)
            ref.dec_ref()
            return
        if self.stack.forwarding:
            router = self.stack.find_router(
                nic_id=0,
                local_address="",
                remote_address=dst,
                network_protocol_number=network_protocol_number,
            )
            if not router:
                self.stack.stats.ip.invalid_addresses_received.increment()
                return
            router.local_link_address = self.link_ep.link_address
            router.remote_link_address = remote_link_addr
            nic: NIC = router.referenced_network_endpoint.nic
            ref: ReferencedNetworkEndpoint = nic.endpoints.get(
                NetworkEndpointID(address=dst)
            )
            if ref and ref.try_inc_ref():
                ref.ep.handle_packet(router, buffer)
                ref.dec_ref()
            else:
                header = Ethernet().from_bytes(eth_data=buffer)
                self.link_ep.write_packet(
                    router, header, buffer, network_protocol_number
                )
            return
        self.stack.stats.ip.invalid_addresses_received.increment()

    def get_ref(
        self, network_protocol_number: int, dst: str
    ) -> Optional[ReferencedNetworkEndpoint]:
        network_endpoint_id = NetworkEndpointID(address=dst)
        ref: Optional[ReferencedNetworkEndpoint] = self.endpoints.get(
            network_endpoint_id
        )
        if ref and ref.try_inc_ref():
            return ref
        promiscuous = self.promiscuous
        if not promiscuous:
            for subnet in self.subnets:
                if subnet.contains(dst):
                    promiscuous = True
                    break

        if promiscuous:
            ref = self.add_address_locked(
                protocol_number=network_protocol_number,
                address=dst,
                primary_endpoint_behavior=NICConst.CAN_BE_PRIMARY_ENDPOINT,
                replace=True,
            )

        if ref:
            ref.holds_insert_ref = False
            return ref
        return None

    def deliver_transport_packet(
        self, router: Router, transport_protocol_number: int, buffer: bytes
    ):
        logger.debug(
            "@nic: Packets are sent to the corresponding transport end according to the transport layer protocol number and transport layer ID."
        )
        state = self.stack.transport_protocols.get(transport_protocol_number)
        if not state:
            self.stack.stats.unknown_protocol_received_packets.increment()
            return
        transport_protocol = state.protocol
        if len(buffer) < transport_protocol.minimum_packet_size:
            logger.debug("@nic: this packet is too short: {}".format(len(buffer)))
            self.stack.stats.malformed_received_packets.increment()
            return
        src_port, dst_port = transport_protocol.parse_ports(buffer)
        if not src_port or not dst_port:
            self.stack.stats.malformed_received_packets.increment()
            return
        transport_endpoint_id = TransportEndpointID(
            local_address=router.local_address,
            local_port=dst_port,
            remote_address=router.remote_address,
            remote_port=src_port,
        )
        if self.de_muxer.deliver_packet(
            router=router,
            transport_protocol_number=transport_protocol_number,
            buffer=buffer,
            transport_endpoint_id=transport_endpoint_id,
        ):
            return
        if self.stack.de_muxer.deliver_packet(
            router=router,
            transport_protocol_number=transport_protocol_number,
            buffer=buffer,
            transport_endpoint_id=transport_endpoint_id,
        ):
            return
        if state.default_handler:
            if state.default_handler(router, transport_endpoint_id, buffer):
                return

        if not transport_protocol.handle_unknown_destination_packet(
            router=router, transport_endpoint_id=transport_endpoint_id, buffer=buffer
        ):
            self.stack.stats.malformed_received_packets.increment()
        return


if __name__ == "__main__":
    from protocol.link.fdbased.endpoint import Endpoint
