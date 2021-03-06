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
