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

        self.configuration_file = None
        if configuration_file:
            self.open_configuration(configuration_file)
        else:
            self.make_default_configuration()

    def open_configuration(self, configuration_file):
        self.configuration_file = configuration_file
        self.global_register = None
        self.pixel_register = None

    def make_default_configuration(self):
        self.global_register = ccpdv4.copy()
        self.pixel_register = {
            "threshold": value = np.full((48, 12), 7, dtype=np.uint8),  # 16 columns (triple row) x 6 rows (double col)
            #"monitor": value = np.full((48,12), 0, dtype=np.uint8),
            "injection": value = np.full((48, 12), 0, dtype=np.uint8)
        }

    def write_chip(self, interface, config=None):
        if isinstance(interface, basestring):
            interface = self.dut[interface]
        if config:
            for reg, value in config.iteritems():
                interface[reg] = value
        interface.write()
        interface.start()  # TODO: check autostart
        while not interface.is_done():
            sleep(0.001)

    def write_global(self):
        self.write_chip('CCPD_GLOBAL', self.global_register)

    def write_pixel(self):
        self.pixel_register
        for col in range(48):
            for row in range(12):
                if row % 2 == 0:
                    in = 'InR'
                elif row % 2 == 1:
                    in = 'InL'
                self.dut['CCPD_CONFIG']['ROW'][5-row/2][in] = self.self.pixel_register['threshold'][col, row]
            if col % 3 == 0:
                ld = 'Ld0'
            elif col % 3 == 1:
                ld = 'Ld0'
            elif col % 3 == 2:
                ld = 'Ld3'
            self.dut['CCPD_CONFIG']['COLUMN'][15-col/3][ld] = 1
            self.write_chip('CCPD_CONFIG')
            self.dut['CCPD_CONFIG']['COLUMN'][15-col/3][ld] = 0
            self.write_chip('CCPD_CONFIG')