import logging
from time import sleep

from pybar.fei4_run_base import Fei4RunBase

ccpdv4_default_config = {
    'BLBias': 1,
    'VNNew': 0,
    'BLRes': 1,
    'ThRes': 0,
    'VNClic': 0,
    'VN': 60,
    'VNFB': 1,
    'VNFoll': 5,
    'VNLoad': 5,
    'VNDAC': 10,
    'VPUp': 8,
    'VPComp': 10,
    'VNCompLd2': 0,
    'VNComp': 10,
    'VNCompLd': 1,
    'VNCOut1': 1,
    'VNCOut2': 1,
    'VNCOut3': 1,
    'VNBuff': 30,
    'VPFoll': 30,
    'VNBias': 0,
    'StripEn': 0
}


class Ccpdv4RunBase(Fei4RunBase):
    '''Basic CCPDv4 run class.

    Base class for scan- / tune- / analyze-class.
    '''

    def write_global(self, config=None):
        if not config:
            config = ccpdv4_default_config
        for reg, value in config.iteritems():
            self.dut['CCPD_GLOBAL'][reg] = value
        self.dut['CCPD_GLOBAL'].write()
        self.dut['CCPD_GLOBAL'].start()
        while not self.dut['CCPD_GLOBAL'].is_done():
            sleep(0.001)

    def init_ccpdv4(self):
        self.dut['CCPD_GLOBAL'].reset()
        self.dut['CCPD_GLOBAL'].set_size(132)
        self.dut['CCPD_GLOBAL'].set_repeat(1)
        self.dut['CCPD_CONFIG'].reset()
        self.dut['CCPD_CONFIG'].set_repeat(1)
        self.dut['CCPD_CONFIG'].set_size(336)
        self.write_global()

    def power_on(self):
        self.dut['V_in'].set_current_limit(1000, unit='mA')  # one for all
        # Vdd, also enabling LVDS transceivers
        self.dut['CCPD_Vdd'].set_voltage(1.8, unit='V')
        self.dut['CCPD_Vdd'].set_enable(True)
        if self.dut["CCPD_Vdd"].get_over_current():
            self.power_off()
            raise Exception('Vdd overcurrent detected')
        # Vssa
        self.dut['CCPD_Vssa'].set_voltage(1.5, unit='V')
        self.dut['CCPD_Vssa'].set_enable(True)
        if self.dut["CCPD_Vssa"].get_over_current():
            self.power_off()
            raise Exception('Vssa overcurrent detected')
        # VGate
        self.dut['CCPD_VGate'].set_voltage(2.1, unit='V')
        self.dut['CCPD_VGate'].set_enable(True)
        if self.dut["CCPD_VGate"].get_over_current():
            self.power_off()
            raise Exception('VGate overcurrent detected')
        # Vcasc
        self.dut['CCPD_Vcasc'].set_voltage(1.1, unit='V')
        # enabling V_in
        self.dut['V_in'].set_voltage(2.1, unit='V')
        self.dut['V_in'].set_enable(True)
        if self.dut["V_in"].get_over_current():
            self.power_off()
            raise Exception('V_in overcurrent detected')

    def power_off(self):
        self.dut['CCPD_VGate'].set_enable(False)
        self.dut['CCPD_Vssa'].set_enable(False)
        self.dut['CCPD_Vdd'].set_enable(False)
        self.dut['V_in'].set_enable(False)
        self.dut["CCPD_Vcasc"].set_voltage(0.0, unit="V")
        self.dut["CCPD_VGate"].set_voltage(0.0, unit="V")
        self.dut["CCPD_Vssa"].set_voltage(0.0, unit="V")
        self.dut["CCPD_Vdd"].set_voltage(0.0, unit="V")
        self.dut["V_in"].set_voltage(0.0, unit="V")

    def init_dut(self):
        self.power_on()
        # enabling readout
        self.dut['rx']['FE'] = 1
        self.dut['rx']['TLU'] = 1
        self.dut['rx']['TDC'] = 1
        self.dut['rx']['CCPD_TDC'] = 1
        self.dut['rx'].write()

    def pre_run(self):
        super(Ccpdv4RunBase, self).pre_run()
        # CCPDv4 specific
        self.init_ccpdv4()
