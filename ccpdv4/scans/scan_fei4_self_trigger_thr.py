import logging
import numpy as np

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
        "scan_timeout": 5,  # timeout for scan after which the scan will be stopped, in seconds
        'send_data': 'tcp://127.0.0.1:5678',
        "scan_parameters": [('Thr', np.arange(0.885, 0.86, -0.001).tolist())],  # list of values, string with calibration file name, None: use 50 GDAC values
        # 0.75
    }

    def configure(self):
        super(FEI4SelfTriggerScan, self).configure()

        logging.info("Scanning %s from %d to %d in %d steps", 'Threshold', self.scan_parameters.Thr[0], self.scan_parameters.Thr[-1], len(self.scan_parameters.Thr))

    def scan(self):
        for threshold in self.scan_parameters.Thr:
            if self.stop_run.is_set():
                break
            self.dut["CCPD_Th"].set_voltage(threshold, unit="V")
            self.set_scan_parameters(Thr=threshold)
            FEI4SelfTriggerScan.scan(self)
            self.clear_err()

    def handle_data(self, data):
        self.raw_data_file.append_item(data, scan_parameters=self.scan_parameters._asdict(), new_file=True, flush=False)


if __name__ == "__main__":
    RunManager('../configuration.yaml').run_run(Fei4SelfTriggerThrScan)
