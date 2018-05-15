# Copyright (C) 2018 Herman Õunapuu
#
# This file is part of linux-gpu-manager.
#
# linux-gpu-manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# linux-gpu-manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with linux-gpu-manager.  If not, see <http://www.gnu.org/licenses/>.

import dbus.service

from modes.pstate.PerformanceGovernor import PerformancePstateGovernor
from modes.pstate.PowersaveGovernor import PowersavePstateGovernor
from modes.pstate.PowersaveLockedGovernor import PowersaveLockedPstateGovernor
from modes.pstate.StockGovernor import StockPstateGovernor


class BetterThermalDaemon(dbus.service.Object):

    def __init__(self, bus_name):
        super().__init__(bus_name, "/ee/ounapuu/BetterThermalDaemon")
        self.current_governor = None
        self.current_governor_name = None

        """
        powersavelocked: stuck at min percentage
        powersave: min to 50% of nonturbo clockspeed
        stock: min to nonturbo clockspeed
        performance: min to max
        performance-locked: lock it at max
        """
        self.controller_modes = ['powersavelocked', 'powersave', 'stock', 'performance', 'performanceoverdrive', 'performancecoolmode']

        self.min_perf_pct = None
        self.max_perf_pct = None
        self.num_pstates = None
        self.turbo_pct = None

        self.init_pstate_driver_info()

        self.start_governor('stock')

    @dbus.service.method("ee.ounapuu.BetterThermalDaemon.setMode", in_signature='s', out_signature='s')
    def set_mode(self, mode):
        if mode in self.controller_modes:
            if mode == self.current_governor_name:
                return "Mode already set to {:s}!".format(mode)
            else:
                self.stop_governor()
                self.start_governor(mode)
                return "Governor set to {:s}".format(mode)
        else:
            return "Invalid mode '{:s}'.".format(mode)

    def start_governor(self, mode):
        self.current_governor = self.get_governor_by_name(mode)
        self.current_governor_name = mode
        self.current_governor.run_governor()

    def stop_governor(self):
        self.current_governor.stop_governor()

    def get_governor_by_name(self, name):
        governors = {
            'stock': StockPstateGovernor(self.min_perf_pct, self.max_perf_pct, self.num_pstates, self.turbo_pct),
            'powersavelocked': PowersaveLockedPstateGovernor(self.min_perf_pct, self.max_perf_pct, self.num_pstates,
                                                             self.turbo_pct),
            'powersave': PowersavePstateGovernor(self.min_perf_pct, self.max_perf_pct, self.num_pstates,
                                                 self.turbo_pct),
            'performance': PerformancePstateGovernor(self.min_perf_pct, self.max_perf_pct, self.num_pstates,
                                                     self.turbo_pct),
        }

        return governors[name]

    def init_pstate_driver_info(self):
        """
        Get the default min-max specs and save them for later use.
        Run once at service start.
        :return:
        """
        paths = {
            "min": "min_perf_pct",
            "max": "max_perf_pct",
            "stepcount": "num_pstates",
            "turbopct": "turbo_pct",
        }
        for level, path in paths.items():
            with open("/sys/devices/system/cpu/intel_pstate/{:s}".format(path)) as f:
                data = int(f.read())
                if level == "min":
                    self.min_perf_pct = data
                if level == "max":
                    self.max_perf_pct = data
                if level == "stepcount":
                    self.num_pstates = data
                if level == "turbopct":
                    self.turbo_pct = data
