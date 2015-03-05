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
        self.global_register = ccpdv4['CCPD_GLOBAL'].copy()
        self.pixel_register = {
            "threshold": np.full((48, 12), 7, dtype=np.uint8),  # 16 columns (triple col) x 6 rows (double row)
#             "monitor": value = np.full((48,12), 0, dtype=np.uint8),
            "injection": np.full((48, 12), 0, dtype=np.uint8)
        }

    def write_chip(self, interface):
        if isinstance(interface, basestring):
            interface = self.dut[interface]
        interface.write()
        interface.start()  # TODO: check autostart
        while not interface.is_done():
            sleep(0.001)

    def write_global(self, register=None, **kwargs):
        if register:
            self.global_register.update(register)
        if kwargs:
            self.global_register.update(kwargs)
        for reg in self.global_register:
            self.dut['CCPD_GLOBAL'][reg] = self.global_register[reg]
        self.write_chip('CCPD_GLOBAL')

    def write_pixel(self, columns=None):
        if not columns:
            columns = range(48)
        # enable comparator
        triple_cols = np.unique(np.array(columns) / 3)
        for triple_col in triple_cols:
            self.dut['CCPD_CONFIG']['COLUMN'][triple_col]['CompEn']
        for col in columns:
            for row in range(12):
                if row % 2 == 0:
                    double_row = 'InR'
                elif row % 2 == 1:
                    double_row = 'InL'
                self.dut['CCPD_CONFIG']['ROW'][5 - row / 2][double_row] = self.pixel_register['threshold'][col, row]
            if col % 3 == 0:
                ld = 'Ld0'
            elif col % 3 == 1:
                ld = 'Ld1'
            elif col % 3 == 2:
                ld = 'Ld2'
            # TOSO: speedup
            self.dut['CCPD_CONFIG']['COLUMN'][15 - col / 3][ld] = 1
            self.write_chip('CCPD_CONFIG')
            self.dut['CCPD_CONFIG']['COLUMN'][15 - col / 3][ld] = 0
            self.write_chip('CCPD_CONFIG')
