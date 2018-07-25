# Copyright (C) 2018 Herman Õunapuu
#
# This file is part of Linux CPU Manager.
#
# Linux CPU Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux CPU Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux CPU Manager.  If not, see <http://www.gnu.org/licenses/>.

import time

from modes.pstate.PstateGovernor import PstateGovernor


class PowersavePstateGovernor(PstateGovernor):
    """
    Runs the CPU at the stock speeds with turbo disabled.
    Throttling is enabled at default package temperature.
    """

    def __init__(self, min_perf_pct, max_perf_pct, num_pstates, turbo_pct):
        super().__init__(min_perf_pct, max_perf_pct, num_pstates, turbo_pct)

        self.governor_name = "POWERSAVE_GOVERNOR"

        self.min_pct_limit = min_perf_pct
        self.max_pct_limit = self.get_max_pct_limit(min_perf_pct, max_perf_pct, num_pstates, turbo_pct)

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

            # apply action
            self.apply_action(self.get_action())

            # print status
            self.get_status()

            # sleep... I need some, too
            time.sleep(self.governor_poll_period_in_seconds)

    def get_max_pct_limit(self, min_perf_pct, max_perf_pct, num_pstates, turbo_pct):
        """
        Gets max pct in order to create powersavings-ish mode for CPU.
        Takes min pct and turbo pct and pretty much gets the centermost pct as the ceiling.
        :return:
        """
        turbo_pct = self.calculate_noturbo_max_pct(min_perf_pct, max_perf_pct, num_pstates, turbo_pct)
        return int(min_perf_pct + ((turbo_pct - min_perf_pct) / 2))
