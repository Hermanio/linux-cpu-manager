# Copyright (C) 2018 Herman Õunapuu
#
# This file is part of Better Thermal Daemon.
#
# Better Thermal Daemon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Better Thermal Daemon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Better Thermal Daemon.  If not, see <http://www.gnu.org/licenses/>.

import multiprocessing
from abc import ABCMeta, abstractmethod


class PstateGovernor(object):
    __metaclass__ = ABCMeta

    def __init__(self, min_perf_pct, max_perf_pct, num_pstates, turbo_pct):
        """
        Init shared components.
        Other governors may want to use multiple temperature levels or different MHz steppings
        or aggressive polling, thus we don't set these here.
        """
        self.pstate_path = "/sys/devices/system/cpu/intel_pstate/"
        self.pstate_governor_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"  # cpu0 safe bet, applies same governor to all cores
        self.package_temperature_path = "/sys/devices/platform/coretemp.0/hwmon/hwmon2/temp1_input"
        self.package_max_temp_path = "/sys/devices/platform/coretemp.0/hwmon/hwmon2/temp1_max"
        self.package_critical_temp_path = "/sys/devices/platform/coretemp.0/hwmon/hwmon2/temp1_crit"

        self.governor_name = None

        self.current_min_pct = min_perf_pct
        self.current_max_pct = max_perf_pct

        self.min_pct_limit = None
        self.max_pct_limit = None

        self.no_turbo = None

        self.governor_thread = None

        self.read_initial_temps()

    @abstractmethod
    def start(self):
        """
        Method containing main loop. Gets called via multiprocess API.
        :return:
        """
        pass

    def get_status(self):
        """
        Returns the current state (min perf pct, max perf pct, no turbo status)
        :return:
        """
        stats = {
            "min_perf_pct": "min_perf_pct",
            "max_perf_pct ": "max_perf_pct",
            "no_turbo": "no_turbo"
        }

        for stat, path in stats.items():
            with open("/sys/devices/system/cpu/intel_pstate/{:s}".format(path)) as f:
                print("{:s}:\t{:s}".format(stat, f.read()), end='')

        print(str(self.current_temperature))
        print()

    def run_governor(self):
        """
        Starts the governor process.
        """
        self.governor_thread = multiprocessing.Process(target=self.start)
        self.governor_thread.start()

    def stop_governor(self):
        """
        Stops the governor main loop from running.
        :return:
        """
        print("Stopping governor {:s}...".format(self.governor_name))
        self.governor_thread.terminate()
        self.governor_thread = None

    def read_initial_temps(self):
        """
        Reads the max and critical temperatures in order to determine the default
        :return:
        """

        with open(self.package_temperature_path, "r") as f:
            self.current_temperature = int(f.read()) / 1000

        with open(self.package_max_temp_path, "r") as f:
            self.package_max_temp = int(f.read()) / 1000

        with open(self.package_critical_temp_path, "r") as f:
            self.package_critical_temp = int(f.read()) / 1000

    def read_current_temps(self):
        """
        Simply reads the current package temperature.
        Alternative to reading all of the core temps and getting the maximum of them.
        Through basic observation the package temperature seems to be the maximum of the individual cores.
        :return:
        """
        with open(self.package_temperature_path, "r") as f:
            self.current_temperature = int(f.read()) / 1000

    def calculate_noturbo_max_pct(self, min_perf_pct, max_perf_pct, num_pstates, turbo_pct):
        """
        Calculates the performance percentage at the turbo clock speed limit.
        Used to allow proper throttling when no_turbo is set to 1, as we need the proper percentages to perform throttling.
        :param min_perf_pct:
        :param max_perf_pct:
        :param num_pstates:
        :param turbo_pct:
        :return:
        """
        percentage_range = max_perf_pct - min_perf_pct
        step_pct = percentage_range / (num_pstates - 1)
        nonturbo_range_pct = (100 - turbo_pct) / 100
        turbo_range_start_as_step_count = nonturbo_range_pct * num_pstates
        turbo_range_as_pct = min_perf_pct + (turbo_range_start_as_step_count * step_pct)
        return int(turbo_range_as_pct)

    def get_action_pct(self):
        return int((self.package_max_temp - self.current_temperature) / 2)

    def apply_action(self, settings):
        for setting, value in settings.items():
            with open(self.pstate_path + str(setting), "w") as f:
                print("Setting {:s} to {:d}".format(setting, int(value)))
                f.write(str(int(value)))

    def get_action(self):
        """
        Apply settings.
        :param min:
        :param stock:
        :param max:
        :return:
        """

        self.current_max_pct = self.current_max_pct + self.get_action_pct()

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

        return settings

    def set_intel_pstate_performance_bias(self, bias):
        if bias in ("powersave", "performance"):
            with open(self.pstate_governor_path, "w") as f:
                print("Setting pstate governor to {:s}".format(bias))
                f.write(bias)
