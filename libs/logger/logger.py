# -*- coding: utf-8 -*-
# @Time : 2022/7/1 17:09
# @Author : Cash111
# @Email : veryperry49@gmail.com
# @File : logger.py
# @Description: None
import logging
from logging import config

config.fileConfig("logging.conf")
logger = logging.getLogger("root")
