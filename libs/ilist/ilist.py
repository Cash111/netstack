# -*- coding: utf-8 -*-
# @Time : 2022/7/1 17:55
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : ilist.py
# @Description: None
import abc
from functools import wraps


class Linker(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def next(self):
        """

        :return:
        """

    @abc.abstractmethod
    def prev(self):
        """

        :return:
        """

    @abc.abstractmethod
    def set_next(self, element):
        """

        :param element:
        :return:
        """

    @abc.abstractmethod
    def set_prev(self, element):
        """

        :param element:
        :return:
        """


class Element(Linker, abc.ABC):
    def __init__(self, value=None):
        self._next = None
        self._prev = None
        self.value = value


class KVElement(Element, abc.ABC):
    def __init__(self, key=None, value=None):
        super(KVElement, self).__init__()
        self._next = None
        self._prev = None
        self.key = key
        self.value = value


class Entry(Element):
    def __init__(self, value=None):
        super(Entry, self).__init__(value)

    def next(self) -> Element:
        return self._next

    def prev(self) -> Element:
        return self._prev

    def set_next(self, element):
        self._next = element

    def set_prev(self, element):
        self._prev = element


class IList(object):

    def __init__(self, node=None):
        self._head: Element = node
        self._tail: Element = None
        self._length = 0

    def is_empty(self):
        return self._head is None

    def front(self):
        return self._head

    def back(self):
        return self._tail

    def append(self, node: Element):
        """
        尾部添加
        :param node:
        :return:
        """
        if self.is_empty():
            self._head = node
            self._tail = node
            self._incr()
            return self
        self._tail.set_next(node)
        node.set_prev(self._tail)
        self._tail = node
        self._incr()
        return self

    def add(self, node: Element):
        """
        头部插入
        :return:
        """
        if self.is_empty():
            self._head = node
            self._incr()
            return self
        self._head.set_prev(node)
        node.set_next(self._head)
        self._head = node
        self._incr()
        return self

    @property
    def length(self):
        """
        获取链表长度
        :return:
        """
        return self._length

    def insert_after(self, target: Element, node: Element):
        """
        节点后插入
        :param target:
        :param node:
        :return:
        """
        _next = target.next()
        node.set_next(_next)
        node.set_prev(target)
        target.set_next(node)
        if _next.value is not None:
            _next.set_prev(node)
        else:
            self._tail = node
        self._incr()

    def insert_before(self, target: Element, node: Element):
        _before = target.prev()
        node.set_next(target)
        node.set_prev(_before)
        target.set_next(node)
        if _before.value is not None:
            _before.set_next(node)
        else:
            self._head = node
        self._incr()

    def remove(self, node: Element):
        """
        :param node:
        :return:
        """
        _next = node.next()
        _prev = node.prev()
        if _prev.value is not None:
            _prev.set_next(_next)
        else:
            self._head = _next

        if _next.value is not None:
            _next.set_prev(_prev)
        else:
            self._tail = node
        self._decr()

    def remove_tail(self):
        self.remove(self._tail)

    def search(self, value):
        """
        查找
        :param value:
        :return:
        """
        cur = self._head
        while cur is not None:
            if cur.value == value:
                return True
            cur = cur.next
        return False

    def travel(self):
        """
        遍历链表
        :return:
        """
        cur = self._head
        while cur is not None:
            yield cur.value
            cur = cur.next

    def _incr(self):
        self._length += 1

    def _decr(self):
        self._length -= 1


if __name__ == '__main__':
    a = Entry(1)
    b = IList()
    b.append(a)
    print(b.length)
    b.add(a)
    print(b.length)
    b.remove(a)
    print(b.length)
    print(b)
