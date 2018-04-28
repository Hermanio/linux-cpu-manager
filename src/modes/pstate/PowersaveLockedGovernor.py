import time

from modes.pstate.PstateGovernor import PstateGovernor


class PowersaveLockedPstateGovernor(PstateGovernor):
    """
    Runs the CPU at the stock speeds with turbo disabled.
    Throttling is enabled at default package temperature.
    """

    def __init__(self, min_perf_pct, max_perf_pct, num_pstates, turbo_pct):
        super().__init__(min_perf_pct, max_perf_pct, num_pstates, turbo_pct)

        self.governor_name = "POWERSAVE_LOCKED_GOVERNOR"

        self.min_pct_limit = min_perf_pct
        self.max_pct_limit = min_perf_pct

        self.no_turbo = 1

        self.governor_poll_period_in_seconds = 5

        self.set_intel_pstate_performance_bias("powersave")


    def start(self):
        """
        Starts the governor main loop.
        :return:
        """

        print("Starting governor {:s}...".format(self.governor_name))

        # main loop
        while True:
            self.apply_action(self.get_action())

            # print status
            self.get_status()

            # sleep... I need some, too
            time.sleep(self.governor_poll_period_in_seconds)