import logging
from time import sleep

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from ccpdv4.ccpdv4_run_base import Ccpdv4RunBase
from pybar.run_manager import RunManager


class Init(Ccpdv4RunBase):
    '''Init scan
    '''
    _default_run_conf = {
        'reg': "VN",
        'values': range(64),
        'channel': 'CCPD_Vssa',
        'unit': 'mA'
    }

    def configure(self):
        pass

    def scan(self):
        logging.info('Starting measurement...')
        self.currents = []
        for val in self.values:
            self.ccpd_register.write_global({self.reg: val})
            sleep(0.2)
            curr = self.dut[self.channel].get_current(unit=self.unit)
            logging.info('%s DAC: %d, %s Current: %.3f%s', self.reg, val, self.channel, curr, self.unit)
            self.currents.append(curr)

    def analyze(self):
        fig = Figure()
        FigureCanvas(fig)
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor('white')
        ax.grid(True)
        ax.plot(self.values, self.currents, 'b.-')
        ax.set_title('%s Current vs. %s DAC' % (self.channel, self.reg))
        ax.set_xlabel('%s DAC [a.u.]' % self.reg)
        ax.set_ylabel('%s Current [%s]' % (self.channel, self.unit))
        ax.set_xlim(0, 64)
        fig.savefig(self.output_filename + '.pdf')

if __name__ == "__main__":
    RunManager('../configuration.yaml').run_run(Init)
