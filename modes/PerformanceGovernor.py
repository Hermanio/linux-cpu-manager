import time

from modes.Action import Action
from modes.Governor import Governor


class PerformanceGovernor(Governor):
    """
    Runs the CPU at the stock speeds with turbo range enabled.
    Throttling is enabled at default package temperature.
    """

    def __init__(self, min_perf_pct, max_perf_pct, num_pstates, turbo_pct):
        super().__init__(min_perf_pct, max_perf_pct, num_pstates, turbo_pct)

        self.governor_name = "PERFORMANCE_GOVERNOR"

        self.low_temp_limit = self.package_max_temp - 10  # low temp at which we can boost the performance
        self.safe_temp_limit = self.package_max_temp  # target temperature
        self.critical_temp_limit = self.package_critical_temp - 10  # 10C headroom, 105C crit is 95C upper bound at which to take action fast.

        self.governor_poll_period_in_seconds = 0.25

        self.min_pct_limit = min_perf_pct
        self.max_pct_limit = max_perf_pct

        self.no_turbo = 0

        self.current_min_pct = min_perf_pct
        self.current_max_pct = max_perf_pct

    def start(self):
        """
        Starts the governor main loop.
        :return:
        """

        print("Starting governor {:s}...".format(self.governor_name))

        # main loop
        while True:
            self.read_current_temps()
            # apply action
            self.apply_action(None)

            # print status
            self.get_status()

            # sleep... I need some, too
            time.sleep(self.governor_poll_period_in_seconds)

    def apply_action(self,action):
        """
        Apply settings.
        :param min:
        :param stock:
        :param max:
        :return:
        """

        self.current_max_pct = self.current_max_pct + self.get_temperature_diff_over_max()

        if self.current_max_pct < self.min_pct_limit:
            self.current_max_pct = self.min_pct_limit

        if self.current_max_pct > self.max_pct_limit:
            self.current_max_pct = self.max_pct_limit

        # min, max, boost
        settings = {
            "min_perf_pct": self.current_min_pct,
            "max_perf_pct": self.current_max_pct,
            "no_turbo": self.no_turbo
        }

        for setting, value in settings.items():
            with open(self.pstate_path + str(setting), "w") as f:
                print("Setting {:s} to {:d}".format(setting, int(value)))
                f.write(str(int(value)))

    def get_temperature_diff_over_max(self):
        return int((self.package_max_temp - self.current_temperature) / 2)
