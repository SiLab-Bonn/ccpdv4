from pybar.scans.tune_stuck_pixel import StuckPixelScan

from ccpdv4.ccpdv4_run_base import Ccpdv4RunBase
from pybar.run_manager import RunManager


class StuckPixelScan(Ccpdv4RunBase, StuckPixelScan):
    pass


if __name__ == "__main__":
    RunManager('../configuration.yaml').run_run(StuckPixelScan)
