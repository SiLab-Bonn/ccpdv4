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
        self.ccpd_register.write_pixel()

    def power_on(self):
        # PWR
        self.dut['V_in'].set_current_limit(0.1, unit='A')  # one for all, max. 1A
        # V_in
        self.dut['V_in'].set_voltage(2.1, unit='V')
        self.dut['V_in'].set_enable(True)
        if self.dut["V_in"].get_over_current():
            self.power_off()
            raise Exception('V_in overcurrent detected')
        # Vdd, also enabling LVDS transceivers
        self.dut['CCPD_Vdd'].set_voltage(1.80, unit='V')
        self.dut['CCPD_Vdd'].set_enable(True)
        if self.dut["CCPD_Vdd"].get_over_current():
            self.power_off()
            raise Exception('Vdd overcurrent detected')
        # Vssa
        self.dut['CCPD_Vssa'].set_voltage(1.50, unit='V')
        self.dut['CCPD_Vssa'].set_enable(True)
        if self.dut["CCPD_Vssa"].get_over_current():
            self.power_off()
            raise Exception('Vssa overcurrent detected')
        # VGate
        self.dut['CCPD_VGate'].set_voltage(2.10, unit='V')
        self.dut['CCPD_VGate'].set_enable(True)
        if self.dut["CCPD_VGate"].get_over_current():
            self.power_off()
            raise Exception('VGate overcurrent detected')
        # VSRC
#         self.dut["CCPD_Vcasc"].set_voltage(1.10, unit="V")  # default: floating, else 1.1V
#         self.dut["CPPD_HVPlus"].set_voltage(1.80, unit="V")  # default: floating, else Vdd
        self.dut["CCPD_BL"].set_voltage(0.80, unit="V")  # default: 0.8V
        self.dut["CCPD_Th"].set_voltage(0.873, unit="V")  # default: 0.90V, note: 100mV difference between V2 and V4
        # INJ, use CCPD_INJ_PULSE
        self.dut['CCPD_Injection_high'].set_voltage(value=0.75, unit="V")
        self.dut['CCPD_Injection_low'].set_voltage(value=0.50, unit="V")

        # Power externally:
        # VPlus: 1.3V
        # VMi0: The amplitude for column 3i is VPlus - VMi0
        # VMi1: The amplitude for column 3i+1 is VPlus - VMi1
        # VMi2: The amplitude for column 3i+2 is VPlus - VMi2

    def power_off(self):
        # VSRC
        self.dut["CCPD_Vcasc"].set_voltage(0.00, unit="V")
        self.dut["CCPD_HVPlus"].set_voltage(0.00, unit="V")
        self.dut["CCPD_BL"].set_voltage(0.00, unit="V")
        self.dut["CCPD_Th"].set_voltage(0.00, unit="V")
        # PWR
        self.dut["CCPD_VGate"].set_voltage(0.00, unit="V")
        self.dut["CCPD_Vssa"].set_voltage(0.00, unit="V")
        self.dut["CCPD_Vdd"].set_voltage(0.00, unit="V")
        self.dut["V_in"].set_voltage(0.00, unit="V")
        self.dut['CCPD_VGate'].set_enable(False)
        self.dut['CCPD_Vssa'].set_enable(False)
        self.dut['CCPD_Vdd'].set_enable(False)
        self.dut['V_in'].set_enable(False)
        # INJ, use CCPD_INJ_PULSE
        self.dut['CCPD_Injection_high'].set_voltage(value=0.00, unit="V")
        self.dut['CCPD_Injection_low'].set_voltage(value=0.00, unit="V")

    def init_dut(self):
        self.power_on()
        # enabling readout
        self.dut['ENABLE_CHANNEL']['FE'] = 1
        self.dut['ENABLE_CHANNEL']['TLU'] = 1
        self.dut['ENABLE_CHANNEL']['TDC'] = 1
        self.dut['ENABLE_CHANNEL']['CCPD_TDC'] = 1
        self.dut['ENABLE_CHANNEL'].write()

    def pre_run(self):
        super(Ccpdv4RunBase, self).pre_run()
        # CCPDv4 specific
        self.init_ccpdv4()
