import logging
from time import sleep

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from ccpdv4.ccpdv4_run_base import Ccpdv4RunBase
from pybar.run_manager import RunManager


class Init(Ccpdv4RunBase):
    '''Init scan
    '''
    _default_run_conf = {}

    def configure(self):
        pass

    def scan(self):
        logging.info('Nothing to do...')

    def analyze(self):
        pass

if __name__ == "__main__":
    RunManager('../configuration.yaml').run_run(Init)
