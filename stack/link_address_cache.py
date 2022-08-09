# -*- coding: utf-8 -*-
# @Time : 2022/7/10 18:41
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : link_address_cache.py
# @Description: None
import time
from libs.ilist.ilist import IList, KVElement
from libs.typing import *
from protocol.tcpip import FullAddress


class LRUCache(object):
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.map = {}
        self.list = IList()

    def get(self, key):
        """
        只要获取了，就把这个节点提到list链表头
        :param key:
        :return:
        """
        if key in self.map:
            node = self.map[key]
            self.list.remove(node)
            self.list.add(node)
            return node.value
        else:
            return -1

    def put(self, key, value):
        """
        如果在map里，把list里的那个节点提到链表头部，map更新映射
        如果不在map里，分两种，一种是超size后把表尾节点删掉，另一种是不超size，相当于添加，把节点放到list表头就行
        :param key:
        :param value:
        :return:
        """
        if key in self.map:
            node = self.map.get(key)
            self.list.remove(node)
            node.value = value
            self.list.add(node)
        else:
            node = KVElement(key, value)
            # 链表缓存已经满了
            if self.list.length >= self.capacity:
                old_node = self.list.remove_tail()
                self.map.pop(old_node.key)

            self.list.add(node)
            self.map[key] = node


class EntryState(object):
    INCOMPLETE: STATE = 0
    READY: STATE = 1
    FAILED: STATE = 2
    EXPIRED: STATE = 3


class LinkAddressEntry(object):
    def __init__(self, address: FullAddress, link_address: LINK_ADDRESS, expiration: TIMESTAMP):
        self.address = address
        self.link_address = link_address
        self.expiration = expiration
        self.s: STATE = -1

    def state(self):
        if self.s != EntryState.EXPIRED and time.time() > self.expiration:
            self.change_state(EntryState.EXPIRED)
        return self.s

    def change_state(self, state: STATE):
        if self.s == state:
            return

        if self.s == EntryState.INCOMPLETE:
            # @TODO:// can do anything here
            pass
        elif self.s in [EntryState.READY, EntryState.FAILED]:
            if state != EntryState.EXPIRED:
                raise Exception("Invalid state transition from {} to {}".format(self.s, state))
        elif self.s == EntryState.EXPIRED:
            raise Exception("Invalid state transition from {} to {}".format(self.s, state))
        else:
            raise Exception("Invalid state {}".format(self.s,))


class LinkAddressCache(object):
    def add(self, address: FullAddress, link_address: LINK_ADDRESS):
        pass
