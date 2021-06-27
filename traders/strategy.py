from traders.signals.signal_type import SignalAction


class Strategy():
    def __init__(self, signals: []):
        self.signals = signals

    def get_action(self, historical_data, close):
        action = SignalAction.WAIT


        votes = []

        # TODO: change from action to desired state: that way if we miss a cross over we'll still trade at first chance.
        for s in self.signals:
            votes.append(s.get_action(historical_data))

        # currently all signals must agree to initiate a trade
        if all(vote == SignalAction.BUY for vote in votes):
            action = SignalAction.BUY
        elif all(vote == SignalAction.SELL for vote in votes):
            action = SignalAction.SELL

        # if action != SignalAction.WAIT:
        #     for s in self.signals:
        #         s.render(historical_data)

        return action
