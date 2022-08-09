# -*- coding: utf-8 -*-
# @Time : 2022/6/30 11:58
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : raw_file.py
# @Description: None
import os
import fcntl

from typing import Iterable, List


class RawFile(object):
    @staticmethod
    def blocking_read(fd: int, max_size: int) -> Iterable:
        """
        :param fd:
        :param max_size:
        :return:
        """
        while True:
            buf = os.read(fd, max_size)
            yield buf

    @staticmethod
    def blocking_readv(fd: int, default_buffer_size: int) -> (bytearray, int):
        """
        Read data from 'fd' to 'buffers'.
        :param fd:
        :param default_buffer_size:
        :return:
        """
        buffers = bytearray()
        total_buffer_size = 0
        buffer_size = default_buffer_size
        # When 'buffer_size' and 'default_buffer_size' do not match, it means that the data has been read.
        while buffer_size == default_buffer_size:
            buffer = [bytearray(default_buffer_size)]
            buffer_size = os.readv(fd, buffer)
            total_buffer_size += buffer_size
            buffers.extend(buffer[0])
        return buffers, total_buffer_size

    @staticmethod
    def set_non_blocking(fd: int):
        """
        set fd non-blocking
        :param fd:
        :return:
        """
        o_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        n_flags = o_flags | os.O_NONBLOCK
        fcntl.fcntl(fd, fcntl.F_SETFL, n_flags)

    @staticmethod
    def non_blocking_write(fd: int, buf: bytearray) -> int:
        """
        :param fd:
        :param buf:
        :return:
        """
        n = os.write(fd, bytes(buf))
        return n
