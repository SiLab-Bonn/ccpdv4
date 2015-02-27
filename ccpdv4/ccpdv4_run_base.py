import logging
from time import time
import re
import os
import sys
import numpy as np
from functools import wraps
from threading import Event, Thread
from Queue import Queue
import tables as tb
from collections import namedtuple, Mapping
from contextlib import contextmanager
import abc
import ast
import inspect
from basil.dut import Dut

from pybar.run_manager import RunAborted
from pybar.fei4_run_base import Fei4RunBase, namedtuple_with_defaults
from pybar.fei4.register import FEI4Register
from pybar.fei4.register_utils import FEI4RegisterUtils, is_fe_ready
from pybar.daq.fifo_readout import FifoReadout, RxSyncError, EightbTenbError, FifoError, NoDataTimeout, StopTimeout
from pybar.daq.fei4_raw_data import open_raw_data_file
from pybar.analysis.analysis_utils import AnalysisError
from pybar.analysis.RawDataConverter.data_struct import NameValue


class Ccpdv4RunBase(Fei4RunBase):
    '''Basic CCPDv4 run class.

    Base class for scan- / tune- / analyze-class.
    '''

    def _init_dut(self):
        self.dut['V_in'].set_current_limit(1000, unit='mA')  # one for all
        # enabling LVDS transceivers
        self.dut['CCPD_Vdd'].set_enable(False)
        self.dut['CCPD_Vdd'].set_voltage(0.0, unit='V')
        self.dut['CCPD_Vdd'].set_enable(True)
        # enabling V_in
        self.dut['V_in'].set_enable(False)
        self.dut['V_in'].set_voltage(2.1, unit='V')
        self.dut['V_in'].set_enable(True)
        # enabling readout
        self.dut['rx']['FE'] = 1
        self.dut['rx']['TLU'] = 1
        self.dut['rx']['TDC'] = 1
        self.dut['rx']['CCPD_TDC'] = 0
        self.dut['rx'].write()
