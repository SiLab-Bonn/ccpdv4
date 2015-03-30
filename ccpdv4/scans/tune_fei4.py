from pybar.scans.tune_fei4 import Fei4Tuning

from ccpdv4.ccpdv4_run_base import Ccpdv4RunBase
from pybar.run_manager import RunManager


class Fei4Tuning(Ccpdv4RunBase, Fei4Tuning):
    _default_run_conf = {
        # tuning parameters
        'send_data': 'tcp://127.0.0.1:5678',
        "target_threshold": 50,  # target threshold
        "target_charge": 280,  # target charge
        "target_tot": 5,  # target ToT
        "global_iterations": 4,  # the number of iterations to do for the global tuning, 0 means only threshold is tuned, negative that no global tuning is done
        "local_iterations": 3,  # the number of iterations to do for the local tuning, 0 means only threshold is tuned, negative that no local tuning is done
        # GDAC
        "gdac_tune_bits": range(7, -1, -1),  # GDAC bits to change during tuning
        "n_injections_gdac": 50,  # number of injections per GDAC bit setting
        "max_delta_threshold": 2,  # minimum difference to the target_threshold to abort the tuning
        "mask_steps_gdac": 3,  # mask
        "enable_mask_steps_gdac": [0],  # mask steps to do per GDAC setting
        # Feedback
        "feedback_tune_bits": range(7, -1, -1),
        "n_injections_feedback": 50,
        "max_delta_tot": 0.1,
        # TDAC
        "tdac_tune_bits": range(4, -1, -1),
        "n_injections_tdac": 100,
        # FDAC
        "fdac_tune_bits": range(3, -1, -1),
        "n_injections_fdac": 30,
        # general
        "enable_shift_masks": ["Enable", "C_High", "C_Low"],  # enable masks shifted during scan
        "disable_shift_masks": [],  # disable masks shifted during scan
        "pulser_dac_correction": False,  # PlsrDAC correction for each double column
        "scan_parameters": [('GDAC', -1), ('TDAC', -1), ('PrmpVbpf', -1), ('FDAC', -1), ('global_step', 0), ('local_step', 0)],
        # plotting
        "make_plots": True,  # plots for all scan steps are created
        "plot_intermediate_steps": False,  # plot intermediate steps (takes time)
        "plots_filename": None,  # file name to store the plot to, if None show on screen
    }


if __name__ == "__main__":
    RunManager('../configuration.yaml').run_run(Fei4Tuning)
