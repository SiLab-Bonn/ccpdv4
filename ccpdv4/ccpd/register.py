import logging
import re
import os
import ast
import numpy as np
import tables as tb
from time import sleep

from ccpdv4.ccpd.ccpd_defaults import ccpdv4

flavors = ('ccpdv4')


class CcpdRegister(object):
    def __init__(self, dut, configuration_file=None):
        self.dut = dut

        if configuration_file:
            self.open_configuration(configuration_file)
        else:
            self.make_default_configuration()

    def open_configuration(self):
        pass

    def make_default_configuration(self):
        self.global_register = ccpdv4.copy()
        self.pixel_register = {}

    def write_chip(self, interface, config):
        if isinstance(interface, basestring):
            interface = self.dut[interface]
        for reg, value in config.iteritems():
            interface[reg] = value
        interface.write()
        interface.start()  # TODO: check autostart
        while not interface.is_done():
            sleep(0.001)

    def write_global(self):
        self.write_chip('CCPD_GLOBAL', self.global_register)
