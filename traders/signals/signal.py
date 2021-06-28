import pandas as pd
import matplotlib.pyplot as plt


from traders.signals.signal_type import SignalAction


class Signal():
    def __init__(self):
        # forces pandas to log all rows/columns
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

        plt.style.use('seaborn')

        self.action_list = []

    def _add_action(self, action: SignalAction, time, close):
        self.action_list.append({
            'action': action,
            'time': time,
            'close': close
        })
