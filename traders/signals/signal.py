import pandas as pd
import matplotlib.pyplot as plt
from traders.signals.signal_action import SignalAction
import numpy as np

class Signal():
    def __init__(self):
        # forces pandas to log all rows/columns
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

        plt.style.use('seaborn')

        self.action_list = []
        self.last_order = None
        self.history = None

    def _add_action(self, action: SignalAction, time, close):
        self.action_list.append({
            'action': action,
            'time': time,
            'close': close,
            'epoch': (time - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        })

    def set_last_order(self, last_order):
        self.last_order = last_order

    def _add_to_history(self, latest_interval):
        if self.history is None:
            self.history = latest_interval.copy(deep=True)
        else:
            self.history = self.history.append(latest_interval.copy(deep=True))