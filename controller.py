import dbus.service

from modes import StockGovernor, PowersaveGovernor, PerformanceGovernor

# TODO set cpufreq governor too for better governor behaviour. if performance then do whatever, push it to max, otherwise push to performance. Check bios level stuff too
from modes.PowersaveLockedGovernor import PowersaveLockedGovernor


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
        self.controller_modes = ['powersavelocked', 'powersave', 'stock', 'performance', 'performance-locked']

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
            'stock': StockGovernor(self.min_perf_pct, self.max_perf_pct, self.num_pstates, self.turbo_pct),
            'powersavelocked': PowersaveLockedGovernor(self.min_perf_pct, self.max_perf_pct, self.num_pstates, self.turbo_pct),
            'powersave': PowersaveGovernor(self.min_perf_pct, self.max_perf_pct, self.num_pstates, self.turbo_pct),
            'performance': PerformanceGovernor(self.min_perf_pct, self.max_perf_pct, self.num_pstates, self.turbo_pct),
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
