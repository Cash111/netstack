#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/6/28 17:47
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : taptun.py
# @Description: None
import os
import fcntl
import socket
import ctypes
import typing
from protocol.errors import CommandError
from config.link.link_const import LinkConst, SysCall


class SockAddr(ctypes.Structure):
    _fields_ = [("sa_family", ctypes.c_ushort), ("sa_data", ctypes.c_char * 14)]


class IfMap(ctypes.Structure):
    _fields_ = [
        ("mem_start", ctypes.c_ulong),
        ("mem_end", ctypes.c_ulong),
        ("base_addr", ctypes.c_ushort),
        ("irq", ctypes.c_char),
        ("dma", ctypes.c_char),
        ("port", ctypes.c_char),
    ]


class IfsIfsu(ctypes.Union):
    _fields_ = [
        ("raw_hdlc", ctypes.c_void_p),
        ("cisco", ctypes.c_void_p),
        ("fr", ctypes.c_void_p),
        ("fr_pvc", ctypes.c_void_p),
        ("fr_pvc_info", ctypes.c_void_p),
        ("sync", ctypes.c_void_p),
        ("te1", ctypes.c_void_p),
    ]


class IfSettings(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint),
        ("size", ctypes.c_uint),
        ("ifs_ifsu", IfsIfsu),
    ]


class IfrIfru(ctypes.Union):
    _fields_ = [
        ("ifru_addr", SockAddr),
        ("ifru_dstaddr", SockAddr),
        ("ifru_broadaddr", SockAddr),
        ("ifru_netmask", SockAddr),
        ("ifru_hwaddr", SockAddr),
        ("ifru_flags", ctypes.c_ushort),
        ("ifru_ivalue", ctypes.c_int),
        ("ifru_mtu", ctypes.c_int),
        ("ifru_map", IfMap),
        ("ifru_slave", ctypes.c_char * LinkConst.IFNAMSIZ),
        ("ifru_newname", ctypes.c_char * LinkConst.IFNAMSIZ),
        ("ifru_data", ctypes.c_void_p),
        ("ifru_settings", IfSettings),
    ]


class IfrIfrn(ctypes.Union):
    _fields_ = [("ifrn_name", ctypes.c_char * LinkConst.IFNAMSIZ)]


class IfReq(ctypes.Structure):
    _fields_ = [("ifr_ifrn", IfrIfrn), ("ifr_ifru", IfrIfru)]


class TunTap(object):
    @staticmethod
    def new_net_dev(name: str, mode: int) -> int:
        if mode == LinkConst.TUN:
            return TunTap._new_tun(name)
        elif mode == LinkConst.TAP:
            return TunTap._new_tap(name)
        else:
            return -1

    @staticmethod
    def set_link_up(device_name: str):
        """
        ip link set <device_name> up
        :param device_name:
        :return:
        """
        command = f"ip link set {device_name} up"
        TunTap._exec(command)

    @staticmethod
    def add_ip(device_name: str, ip: str):
        """
        ip addr add 192.168.1.1 dev tap0
        :param device_name:
        :param ip:
        :return:
        """
        command = f"ip addr add {ip} dev {device_name}"
        TunTap._exec(command)

    @staticmethod
    def set_route(name: str, cidr: str):
        """
        ip route add 192.168.1.0/24 dev tap0
        :param name:
        :param cidr:
        :return:
        """
        command = f"ip route add {cidr} dev {name}"
        TunTap._exec(command)

    @staticmethod
    def get_hardware_addr(device_name: str) -> typing.Optional[bytearray]:
        """
        获取虚拟网卡MAC地址
        :param device_name: 虚拟网卡名
        :return:
        """
        sock_fd = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM, 0)
        if sock_fd.fileno() < 0:
            return None
        ifr = IfReq()
        ctypes.memset(ctypes.byref(ifr), 0, ctypes.sizeof(ifr))
        ifr.ifr_ifrn.ifrn_name = device_name.encode("utf-8")
        try:
            fcntl.ioctl(sock_fd.fileno(), SysCall.SIOCGIFHWADDR, ifr)
        except Exception as e:
            print("err: ", e)
            os.close(sock_fd.fileno())
            return None
        mac = bytearray()
        for ch in ifr.ifr_ifru.ifru_hwaddr.sa_data:
            mac.append(ch)
        os.close(sock_fd.fileno())
        return mac

    @staticmethod
    def _exec(command: str):
        res = os.system(command)
        if res != 0:
            raise CommandError("command exec failed: {}".format(command))

    @staticmethod
    def _new_tap(name) -> int:
        return TunTap._open(name, SysCall.IFF_TAP | SysCall.IFF_NO_PI)

    @staticmethod
    def _new_tun(name) -> int:
        return TunTap._open(name, SysCall.IFF_TUN | SysCall.IFF_NO_PI)
    
    @staticmethod
    def _open(name, flags) -> int:
        if not name:
            return -1
        fd = os.open("/dev/net/tun", os.O_RDWR)
        r = IfReq()
        ctypes.memset(ctypes.byref(r), 0, ctypes.sizeof(r))
        r.ifr_ifru.ifru_flags |= flags
        r.ifr_ifrn.ifrn_name = name.encode("utf-8")
        try:
            fcntl.ioctl(fd, SysCall.TUNSETIFF, r)
        except Exception as e:
            print("err:", e)
            os.close(fd)
            return -1
        return fd


if __name__ == "__main__":
    from protocol.link.raw_file.raw_file import RawFile
    from utils.format_utils import FormatUtils
    from config.network.network_const import ARPConst
    from protocol.header.ethernet import Ethernet
    _name = "tap0"
    _fd = TunTap.new_net_dev(_name, LinkConst.TAP)
    _max_size = 4096
    TunTap.set_link_up(_name)
    route = "192.168.1.0/24"
    TunTap.set_route(_name, route)

    for _buf in RawFile.blocking_read(_fd, _max_size):
        if not _buf:
            break
        eth = Ethernet()
        eth.from_bytes(_buf)
        print(eth.dst_addr)
        print(eth.src_addr)
        print(eth.type)
        if FormatUtils.hex_to_int(bytes(eth.type)) == ARPConst.PROTOCOL_NUMBER:
            print("got arp request")
        print("read {} bytes from buf".format(len(_buf)))
