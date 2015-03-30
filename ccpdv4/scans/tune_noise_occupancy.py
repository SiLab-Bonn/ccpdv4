from pybar.scans.tune_noise_occupancy import NoiseOccupancyScan

from ccpdv4.ccpdv4_run_base import Ccpdv4RunBase
from pybar.run_manager import RunManager


class NoiseOccupancyScan(Ccpdv4RunBase, NoiseOccupancyScan):
    _default_run_conf = {
        "occupancy_limit": 0,  # 0 will mask any pixel with occupancy greater than zero
        "n_triggers": 10000000,  # total number of triggers which will be sent to the FE. From 1 to 4294967295 (32-bit unsigned int).
        "trig_count": 1,  # FE global register Trig_Count
        "trigger_rate_limit": 500,  # artificially limiting the trigger rate, in BCs (25ns)
        "disable_for_mask": ['Enable'],  # list of masks for which noisy pixels will be disabled
        "enable_for_mask": ['Imon'],  # list of masks for which noisy pixels will be disabled
        "col_span": [1, 80],  # defining active column interval, 2-tuple, from 1 to 80
        "row_span": [1, 336],  # defining active row interval, 2-tuple, from 1 to 336
        "overwrite_enable_mask": False,  # if True, use col_span and row_span to define an active region regardless of the Enable pixel register. If False, use col_span and row_span to define active region by also taking Enable pixel register into account.
        "use_enable_mask_for_imon": False,  # if True, apply inverted Enable pixel mask to Imon pixel mask
        "no_data_timeout": 10,  # no data timeout after which the scan will be aborted, in seconds
        "overwrite_mask": False  # if True, overwrite existing masks
    }


if __name__ == "__main__":
    RunManager('../configuration.yaml').run_run(NoiseOccupancyScan)
