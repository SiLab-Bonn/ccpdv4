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
        self.dut['V_in'].set_current_limit(1000, unit='mA')  # one for all, max. 1A
        # V_in
#         self.dut['V_in'].set_voltage(2.1, unit='V')
#         self.dut['V_in'].set_enable(True)
#         if self.dut["V_in"].get_over_current():
#             self.power_off()
#             raise Exception('V_in overcurrent detected')
        # Vdd, also enabling LVDS transceivers
        self.dut['CCPD_Vdda'].set_voltage(1.8, unit='V')
        self.dut['CCPD_Vdda'].set_enable(True)
        if self.dut["CCPD_Vdda"].get_over_current():
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
        # VSRC
        self.dut["CCPD_Vcasc"].set_voltage(0.0, unit="V")  # TODO: 1.1V?
        self.dut["CPPD_HVPlus"].set_voltage(0.0, unit="V")  # TODO: fix value
        self.dut["CCPD_BL"].set_voltage(0.8, unit="V")  # TODO: 0.8V?
        self.dut["CCPD_Th"].set_voltage(0.95, unit="V")  # TODO: 0.85V? 100mV difference between V2 and V4
        # ISRC
        self.dut["CPPD_VN"].set_current(0.0, unit="uA")  # TODO: fix value
        # INJ, use CCPD_INJ_PULSE
        self.dut['CCPD_Injection_high'].set_voltage(value=0.75, unit="V")
        self.dut['CCPD_Injection_low'].set_voltage(value=0.5, unit="V")

    def power_off(self):
        # VSRC
        self.dut["CCPD_Vcasc"].set_voltage(0.0, unit="V")
        self.dut["CCPD_HVPlus"].set_voltage(0.0, unit="V")
        self.dut["CCPD_BL"].set_voltage(0.0, unit="V")
        self.dut["CCPD_Th"].set_voltage(0.0, unit="V")
        # ISRC
        self.dut["CPPD_VN"].set_current(0.0, unit="uA")
        # PWR
        self.dut["CCPD_VGate"].set_voltage(0.0, unit="V")
        self.dut["CCPD_Vssa"].set_voltage(0.0, unit="V")
        self.dut["CCPD_Vdda"].set_voltage(0.0, unit="V")
        self.dut["V_in"].set_voltage(0.0, unit="V")
        self.dut['CCPD_VGate'].set_enable(False)
        self.dut['CCPD_Vssa'].set_enable(False)
        self.dut['CCPD_Vdda'].set_enable(False)
        self.dut['V_in'].set_enable(False)
        # INJ, use CCPD_INJ_PULSE
        self.dut['CCPD_Injection_high'].set_voltage(value=0.0, unit="V")
        self.dut['CCPD_Injection_low'].set_voltage(value=0.0, unit="V")

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
