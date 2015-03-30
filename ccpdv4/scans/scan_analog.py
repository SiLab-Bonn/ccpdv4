import logging
import numpy as np
from time import sleep, time
import progressbar

from pybar.scans.scan_fei4_self_trigger import FEI4SelfTriggerScan

from ccpdv4.ccpdv4_run_base import Ccpdv4RunBase
from pybar.run_manager import RunManager


class Fei4SelfTriggerThrScan(Ccpdv4RunBase, FEI4SelfTriggerScan):

    '''External trigger scan with FE-I4 and adjustable GDAC range

    For use with external scintillator (user RX0), TLU (use RJ45), USBpix self-trigger (loop back TX2 into RX0.)
    '''
    _default_run_conf = {
        "trig_count": 4,  # FE-I4 trigger count, number of consecutive BCs, from 0 to 15
        "trigger_latency": 239,  # FE-I4 trigger latency, in BCs, external scintillator / TLU / HitOR: 232, USBpix self-trigger: 220, from 0 to 255
        "col_span": [1, 80],  # defining active column interval, 2-tuple, from 1 to 80
        "row_span": [1, 336],  # defining active row interval, 2-tuple, from 1 to 336
        "overwrite_enable_mask": False,  # if True, use col_span and row_span to define an active region regardless of the Enable pixel register. If False, use col_span and row_span to define active region by also taking Enable pixel register into account.
        "use_enable_mask_for_imon": True,  # if True, apply inverted Enable pixel mask to Imon pixel mask
        "no_data_timeout": 10,  # no data timeout after which the scan will be aborted, in seconds
        "scan_timeout": 10,  # timeout for scan after which the scan will be stopped, in seconds
        'send_data': 'tcp://127.0.0.1:5678',
#         "scan_parameters": [('Thr', np.arange(0.885, 0.86, -0.001).tolist())],  # list of values, string with calibration file name, None: use 50 GDAC values
        # 0.75
    }

    def set_pulser(self, delay=10000, period=100, repeat=10):
        self.dut['CCPD_Injection_high'].set_voltage(value=0.7, unit="V")
        self.dut['CCPD_Injection_low'].set_voltage(value=0.1, unit="V")
        self.dut['CCPD_INJ_PULSE'].RESET
        self.dut['CCPD_INJ_PULSE'].DELAY = period / 2
        self.dut['CCPD_INJ_PULSE'].WIDTH = period - period / 2 + 1
        self.dut['CCPD_INJ_PULSE'].REPEAT = repeat
        self.dut['CCPD_INJ_PULSE'].EN = False

    def start_pulser(self):
        self.dut['CCPD_INJ_PULSE'].start()
#         while not self.dut['CCPD_INJ_PULSE'].is_done():
#             sleep(0.001)

    def configure(self):
        super(FEI4SelfTriggerScan, self).configure()
        self.set_pulser()

    def scan(self):
        for bit in [2]:#, 2, 4, 8, 16, 32]:
            print bit
            if self.stop_run.is_set():
                break
            self.ccpd_register.set_injection(bit)
            self.ccpd_register.write_pixel()
            with self.readout():
                self.start_pulser()
                got_data = False
                start = time()
                while not self.stop_run.wait(1.0):
                    if self.dut['CCPD_INJ_PULSE'].is_done():
                        break
                    if not got_data:
                        if self.fifo_readout.data_words_per_second() > 0:
                            got_data = True
                            logging.info('Taking data...')
                            self.progressbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='*', left='|', right='|'), ' ', progressbar.Timer()], maxval=self.scan_timeout, poll=10, term_width=80).start()
                    else:
                        try:
                            self.progressbar.update(time() - start)
                        except ValueError:
                            pass
            self.clear_err()
        self.dut['CCPD_INJ_PULSE'].set_en(False)

    def handle_data(self, data):
        self.raw_data_file.append_item(data, scan_parameters=None, new_file=True, flush=False)


if __name__ == "__main__":
    RunManager('../configuration.yaml').run_run(Fei4SelfTriggerThrScan)
