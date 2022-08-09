# -*- coding: utf-8 -*-
# @Time : 2022/7/1 10:31
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : endpoint.py
# @Description: None
__all__ = ["Options", "Endpoint"]

import typing

from libs.logger import logger
from config.link.link_const import LinkConst
from config.stack.stack_const import StackConst
from stack.registration import LinkEndpoint, register_link_endpoint
from stack.route import Router
from protocol.header.ethernet import Ethernet
from libs.buffer.view import View
from protocol.link.raw_file.raw_file import RawFile


class Options(object):
    def __init__(
        self,
        fd: int = -1,
        mtu: int = -1,
        closed_func: typing.Callable = None,
        link_address: bytearray = None,
        resolution_required: bool = False,
        save_restore: bool = False,
        checksum_offload: bool = False,
        disconnect_ok: bool = False,
        handle_local: bool = False
    ):
        self.fd = fd
        self.mtu = mtu
        self.closed_func = closed_func
        self.link_address = link_address
        self.resolution_required = resolution_required
        self.save_restore = save_restore
        self.checksum_offload = checksum_offload
        self.disconnect_ok = disconnect_ok
        self.handle_local = handle_local

    def new_link_endpoint(self) -> int:
        RawFile.set_non_blocking(self.fd)

        caps = 0
        if self.resolution_required:
            caps |= StackConst.CAPABILITY_RESOLUTION_REQUIRED
        elif self.checksum_offload:
            caps |= StackConst.CAPABILITY_CHECKSUM_OFFLOAD
        elif self.save_restore:
            caps |= StackConst.CAPABILITY_SAVE_RESTORE
        elif self.disconnect_ok:
            caps |= StackConst.CAPABILITY_DISCONNECT_OK

        endpoint = Endpoint(
            opts=self,
            header_size=LinkConst.ETH_MIN_SIZE
        )
        logger.info("Registers link layer devices")
        return register_link_endpoint(link_ep=endpoint)


class Endpoint(LinkEndpoint):
    def __init__(self, opts: Options, header_size: LinkConst.ETH_MIN_SIZE):
        self.opts = opts
        self.caps = self._caps()
        self.header_size = header_size
        self.dispatcher = None

    @property
    def mtu(self) -> int:
        return self.opts.mtu

    @property
    def capabilities(self) -> int:
        return self.caps

    @property
    def max_header_length(self) -> int:
        return self.header_size

    @property
    def link_address(self) -> bytearray:
        return self.opts.link_address

    def write_packet(self, router: Router, header: Ethernet, payload: View, protocol: int):
        eth_header = Ethernet(
            dst_addr=router.remote_link_address,
            src_addr=router.local_link_address or self.link_address,
            eth_type=bytearray(bytes.fromhex("%02x" % protocol))
        )
        return RawFile.non_blocking_write(self.opts.fd, eth_header.encode())

    def attach(self, dispatcher):
        self.dispatcher = dispatcher
        self.dispatch_loop()

    @property
    def is_attach(self) -> bool:
        return self.dispatcher is not None

    def dispatch_loop(self):
        logger.info("@link fdbased: receive data from NIC with `dispatch`")
        while True:
            dispatch_stat = self.dispatch()
            if not dispatch_stat:
                continue

    def dispatch(self) -> bool:
        buffers, total_buffer_size = RawFile.blocking_readv(self.opts.fd, 128)
        logger.info("@link fdbased: read %d bytes from NIC" % len(buffers))
        if len(buffers) < self.header_size:
            logger.warning("@link fdbased: read %d bytes < header bytest %d，丢弃数据", len(buffers), self.header_size)
            return False
        eth = Ethernet().from_bytes(buffers)
        eth_type = eth.type
        remote_link_addr = eth.dst_addr
        local_link_addr = eth.src_addr
        logger.info("@link fdbased: parsed ethernet: type: {}, remote: {}, local: {}".format(eth_type, remote_link_addr, local_link_addr))
        buf = Ethernet.trim_front(buffers, self.header_size)
        self.dispatcher.deliver_network_packet(self, remote_link_addr, local_link_addr, eth_type, buf)
        return True

    def _caps(self):
        caps = 0
        const_cap = 0
        if self.opts.save_restore:
            const_cap = StackConst.CAPABILITY_SAVE_RESTORE
        elif self.opts.resolution_required:
            const_cap = StackConst.CAPABILITY_RESOLUTION_REQUIRED
        elif self.opts.disconnect_ok:
            const_cap = StackConst.CAPABILITY_DISCONNECT_OK
        elif self.opts.checksum_offload:
            const_cap = StackConst.CAPABILITY_CHECKSUM_OFFLOAD
        caps |= const_cap
        return caps

    def _init_buffers(self) -> list:
        buffers = []
        for buf_config in LinkConst.BUF_CONFIG:
            buffers.append(bytearray(buf_config))
        return buffers
