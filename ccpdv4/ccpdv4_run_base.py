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

    def _run(self):
        self.socket_addr = self._run_conf['send_data']
        if self.socket_addr:
            logging.info('Send data to %s' % self.socket_addr)
        if 'scan_parameters' in self.run_conf:
            if isinstance(self.run_conf['scan_parameters'], basestring):
                self.run_conf['scan_parameters'] = ast.literal_eval(self.run_conf['scan_parameters'])
            sp = namedtuple('scan_parameters', field_names=zip(*self.run_conf['scan_parameters'])[0])
            self.scan_parameters = sp(*zip(*self.run_conf['scan_parameters'])[1])
        else:
            sp = namedtuple_with_defaults('scan_parameters', field_names=[])
            self.scan_parameters = sp()
        logging.info('Scan parameter(s): %s' % (', '.join(['%s=%s' % (key, value) for (key, value) in self.scan_parameters._asdict().items()]) if self.scan_parameters else 'None'))

        try:
            last_configuration = self._get_configuration()
            if 'fe_configuration' in self.conf and self.conf['fe_configuration']:
                if not isinstance(self.conf['fe_configuration'], FEI4Register):
                    if isinstance(self.conf['fe_configuration'], basestring):
                        if os.path.isabs(self.conf['fe_configuration']):
                            fe_configuration = self.conf['fe_configuration']
                        else:
                            fe_configuration = os.path.join(self.conf['working_dir'], self.conf['fe_configuration'])
                        self._conf['fe_configuration'] = FEI4Register(configuration_file=fe_configuration)
                    elif isinstance(self.conf['fe_configuration'], (int, long)) and self.conf['fe_configuration'] >= 0:
                        self._conf['fe_configuration'] = FEI4Register(configuration_file=self._get_configuration(self.conf['fe_configuration']))
                    else:
                        self._conf['fe_configuration'] = FEI4Register(configuration_file=self._get_configuration())
                else:
                    pass  # do nothing, already initialized
            elif last_configuration:
                self._conf['fe_configuration'] = FEI4Register(configuration_file=last_configuration)
            else:
                if 'chip_address' in self.conf and isinstance(self.conf['chip_address'], (int, long)):
                    chip_address = self.conf['chip_address']
                    broadcast = False
                else:
                    chip_address = 0
                    broadcast = True
                if 'fe_flavor' in self.conf and self.conf['fe_flavor']:
                    self._conf['fe_configuration'] = FEI4Register(fe_type=self.conf['fe_flavor'], chip_address=chip_address, broadcast=broadcast)
                else:
                    raise ValueError('No valid configuration found')

            if not isinstance(self.conf['dut'], Dut):
                if isinstance(self.conf['dut'], basestring):
                    if os.path.isabs(self.conf['dut']):
                        dut = self.conf['dut']
                    else:
                        dut = os.path.join(self.conf['working_dir'], self.conf['dut'])
                    self._conf['dut'] = Dut(dut)
                else:
                    self._conf['dut'] = Dut(self.conf['dut'])
                module_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
                if 'dut_configuration' in self.conf and self.conf['dut_configuration']:
                    if isinstance(self.conf['dut_configuration'], basestring):
                        if os.path.isabs(self.conf['dut_configuration']):
                            dut_configuration = self.conf['dut_configuration']
                        else:
                            dut_configuration = os.path.join(self.conf['working_dir'], self.conf['dut_configuration'])
                        self.dut.init(dut_configuration)
                    else:
                        self.dut.init(self.conf['dut_configuration'])
                elif self.dut.name == 'mio_gpac':
                    self.dut.init(os.path.join(module_path, 'dut_configuration_mio_ccpdv4.yaml'))
                else:
                    logging.warning('Omit initialization of DUT')
                if self.dut.name == 'mio_gpac':
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
                else:
                    logging.warning('Unknown DUT name: %s. DUT may not be set up properly' % self.dut.name)

            else:
                pass  # do nothing, already initialized

            if not self.fifo_readout:
                self.fifo_readout = FifoReadout(self.dut)
            if not self.register_utils:
                self.register_utils = FEI4RegisterUtils(self.dut, self.register)
            with open_raw_data_file(filename=self.output_filename, mode='w', title=self.run_id, scan_parameters=self.scan_parameters._asdict(), socket_addr=self.socket_addr) as self.raw_data_file:
                self.save_configuration_dict(self.raw_data_file.h5_file, 'conf', self.conf)
                self.save_configuration_dict(self.raw_data_file.h5_file, 'run_conf', self.run_conf)
                self.register_utils.global_reset()
                self.register_utils.configure_all()
                if is_fe_ready(self):
                    reset_service_records = False
                else:
                    reset_service_records = True
                self.register_utils.reset_bunch_counter()
                self.register_utils.reset_event_counter()
                if reset_service_records:
                    # resetting service records must be done once after power up
                    self.register_utils.reset_service_records()
                with self.register.restored(name=self.run_number):
                    self.configure()
                    self.register.save_configuration(self.raw_data_file.h5_file)
                    self.fifo_readout.reset_rx()
                    self.fifo_readout.reset_sram_fifo()
                    self.fifo_readout.print_readout_status()
                    self.scan()
        except Exception:
            self.handle_err(sys.exc_info())
        else:
            try:
                if self.abort_run.is_set():
                    raise RunAborted('Omitting data analysis: run was aborted')
                self.analyze()
            except AnalysisError as e:
                logging.error('Analysis of data failed: %s' % e)
            except Exception:
                self.handle_err(sys.exc_info())
            else:
                self.register.save_configuration(self.output_filename)
        finally:
            self.raw_data_file = None
            try:
                self.fifo_readout.print_readout_status()
            except Exception:
                pass
            try:
                self.dut['USB'].close()  # free USB resources
            except Exception:
                logging.error('Cannot close USB device')
        if not self.err_queue.empty():
            exc = self.err_queue.get()
            if isinstance(exc[1], (RxSyncError, EightbTenbError, FifoError, NoDataTimeout, StopTimeout)):
                raise RunAborted(exc[1])
            else:
                raise exc[0], exc[1], exc[2]
