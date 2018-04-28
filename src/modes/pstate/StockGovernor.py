import time

from modes.pstate.PstateGovernor import PstateGovernor


class StockPstateGovernor(PstateGovernor):
    """
    Runs the CPU at the stock speeds with turbo disabled.
    Throttling is enabled at default package temperature.
    """

    def __init__(self, min_perf_pct, max_perf_pct, num_pstates, turbo_pct):
        super().__init__(min_perf_pct, max_perf_pct, num_pstates, turbo_pct)

        self.governor_name = "STOCK_GOVERNOR"

        self.min_pct_limit = min_perf_pct
        self.max_pct_limit = self.calculate_noturbo_max_pct(min_perf_pct, max_perf_pct, num_pstates, turbo_pct)

        self.no_turbo = 1

        self.current_min_pct = min_perf_pct
        self.current_max_pct = min_perf_pct

        self.governor_poll_period_in_seconds = 0.25

        self.set_intel_pstate_performance_bias("powersave")

    def start(self):
        """
        Starts the governor main loop.
        :return:
        """

        print("Starting governor {:s}...".format(self.governor_name))

        # main loop
        while True:
            self.read_current_temps()

            self.apply_action(self.get_action())

            # print status
            self.get_status()

            # sleep... I need some, too
            time.sleep(self.governor_poll_period_in_seconds)
