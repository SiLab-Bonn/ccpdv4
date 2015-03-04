import logging

from pybar.fei4_run_base import Fei4RunBase
from ccpdv4.ccpd.register import CcpdRegister


class Ccpdv4RunBase(Fei4RunBase):
    '''Basic CCPDv4 run class.

    Base class for scan- / tune- / analyze-class.
    '''
    def init_ccpdv4(self):
        self.ccpd_register = CcpdRegister(self.dut, configuration_file=None)
        self.ccpd_register.write_global()

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
