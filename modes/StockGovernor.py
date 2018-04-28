import time

from modes.Action import Action
from modes.Governor import Governor


class StockGovernor(Governor):
    """
    Runs the CPU at the stock speeds with turbo disabled.
    Throttling is enabled at default package temperature.
    """

    def __init__(self, min_perf_pct, max_perf_pct, num_pstates, turbo_pct):
        super().__init__(min_perf_pct, max_perf_pct, num_pstates, turbo_pct)

        self.governor_name = "STOCK_GOVERNOR"

        self.low_temp_limit = self.package_max_temp - 20  # low temp at which we can boost the performance
        self.safe_temp_limit = self.package_max_temp  # target temperature
        self.critical_temp_limit = self.package_critical_temp - 10  # 10C headroom, 105C crit is 95C upper bound at which to take action fast.

        self.small_pct_stepping = 1
        self.big_pct_stepping = 3

        self.min_pct_limit = min_perf_pct
        self.max_pct_limit = self.calculate_noturbo_max_pct(min_perf_pct, max_perf_pct, num_pstates, turbo_pct)

        self.no_turbo = 1

        self.current_min_pct = min_perf_pct
        self.current_max_pct = min_perf_pct

        self.governor_poll_period_in_seconds = 0.25

    def start(self):
        """
        Starts the governor main loop.
        :return:
        """

        print("Starting governor {:s}...".format(self.governor_name))

        # main loop
        while True:
            self.read_current_temps()

            # get action
            action = self.decide_action()

            # apply action
            self.apply_action(action)

            # print status
            self.get_status()

            # sleep... I need some, too
            time.sleep(self.governor_poll_period_in_seconds)

    def apply_action(self, action):
        """
        Apply settings.
        :param min:
        :param stock:
        :param max:
        :return:
        """
        if action == Action.THROTTLE_MODERATE:
            clock_change = -self.small_pct_stepping
        elif action == Action.THROTTLE_CRITICAL:
            clock_change = -self.big_pct_stepping
        elif action == Action.BOOST_MODERATE:
            clock_change = self.small_pct_stepping
        elif action == Action.BOOST_CRITICAL:
            clock_change = self.big_pct_stepping
        elif action == Action.NO_OP:
            clock_change = 0
        else:
            clock_change = 0

        self.current_max_pct = self.current_max_pct + clock_change

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
                print("Setting {:s} to {:d}".format(setting, value))
                f.write(str(value))

    def decide_action(self):
        # test criticals first
        if self.current_temperature > self.critical_temp_limit:
            return Action.THROTTLE_CRITICAL

        if self.current_temperature > self.safe_temp_limit:
            return Action.THROTTLE_MODERATE

        if self.current_temperature < self.low_temp_limit:
            return Action.BOOST_CRITICAL

        if self.current_temperature < self.safe_temp_limit:
            return Action.BOOST_MODERATE

        return Action.NO_OP


