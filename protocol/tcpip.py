# -*- coding: utf-8 -*-
# @Time : 2022/6/30 15:39
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : tcpip.py
# @Description: None
from libs.typing import *


class LinkAddress(str):
    pass


class Address(str):
    pass


class FullAddress(object):
    def __init__(self, nic_id: NIC_ID, address: Address, port: int):
        self.nic_id = nic_id
        self.address = address
        self.port = port

    def __str__(self):
        return f"{self.nic_id}:{self.address}:{self.port}"


class Subnet(object):
    address: str = None
    address_mask: List[int] = None

    @classmethod
    def new_subnet(cls, address, address_mask: List[int]):
        cls.address = address
        cls.address_mask = address_mask
        return cls

    def contains(self, address: str) -> bool:
        if len(address) != len(self.address):
            return False
        if address != self.address:
            return False
        return True


class StatsCounter(object):
    def __init__(self):
        self._count: int = 0

    def increment(self):
        self.increment_by(1)

    def increment_by(self, value):
        self._count += value

    def value(self) -> int:
        return self._count


class IPStats(object):
    def __init__(self):
        self.packets_received = StatsCounter()
        self.invalid_addresses_received = StatsCounter()
        self.packets_delivered = StatsCounter()
        self.packets_sent = StatsCounter()
        self.outgoing_packet_errors = StatsCounter()


class TCPStats(object):
    def __init__(self):
        self.active_connection_openings = StatsCounter()
        self.passive_connection_openings = StatsCounter()
        self.failed_connection_attempts = StatsCounter()
        self.valid_segments_received = StatsCounter()
        self.invalid_segments_received = StatsCounter()
        self.segments_sent = StatsCounter()
        self.resets_sent = StatsCounter()
        self.resets_received = StatsCounter()


class UDPStats(object):
    def __init__(self):
        self.packets_received = StatsCounter()
        self.unknown_port_errors = StatsCounter()
        self.receive_buffer_errors = StatsCounter()
        self.malformed_packets_received = StatsCounter()
        self.packets_sent = StatsCounter()


class Stats(object):
    def __init__(self):
        self.unknown_protocol_received_packets = StatsCounter()
        self.malformed_received_packets = StatsCounter()
        self.dropped_packets = StatsCounter()
        self.ip = IPStats()
        self.tcp = TCPStats()
        self.udp = UDPStats()


class Route(object):
    def __init__(
        self, destination: str = "", mask: str = "", gateway: str = "", nic_id: int = -1
    ):
        self.destination = destination
        self.mask = mask
        self.gateway = gateway
        self.nic_id = nic_id

    def match(self, address: str) -> bool:
        if len(address) != len(self.destination):
            return False
        address_split = [int(i) for i in address.split(".")]
        dst_split = [int(i) for i in self.destination.split(".")]
        mask_split = [int(i) for i in self.mask.split(".")]
        for index in range(len(dst_split)):
            if address_split[index] & mask_split[index] != dst_split[index]:
                return False
        return True


class Clock(object):
    pass


class Endpoint(object):
    pass
