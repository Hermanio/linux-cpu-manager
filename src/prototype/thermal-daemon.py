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

RUN_CYCLE_LENGTH_IN_SECONDS = 1.0

FAN_CONTROL_ENABLED = False

SAFE_TEMPERATURE = 80
TARGET_TEMPERATURE = 90
CRITICAL_TEMPERATURE = 95

MIN_CLOCK_PCT = 32
MAX_CLOCK_PCT = 100
CURRENT_CLOCK = 100

THROTTLE_CRITICAL = -5
THROTTLE_MODERATE = -1

INCREASE_MODERATE = 1
INCREASE_BOOST = 5

NO_TURBO_STATE_FILE = "/sys/devices/system/cpu/intel_pstate/no_turbo"
MAX_CLOCK_PCT_FILE = "/sys/devices/system/cpu/intel_pstate/max_perf_pct"
PACKAGE_TEMPERATURE_FILE = "/sys/class/hwmon/hwmon2/temp1_input"
IBM_FAN_FILE = "/proc/acpi/ibm/fan"


def get_package_temp():
    with open(PACKAGE_TEMPERATURE_FILE, 'r') as f:
        return int(f.readline()) / 1000


def get_clock_percentage_diff(current_temperature):
    if current_temperature > CRITICAL_TEMPERATURE:
        temperature_difference = THROTTLE_CRITICAL

    elif current_temperature > TARGET_TEMPERATURE:
        temperature_difference = THROTTLE_MODERATE

    elif current_temperature > SAFE_TEMPERATURE:
        temperature_difference = INCREASE_MODERATE

    else:
        temperature_difference = INCREASE_BOOST

    return temperature_difference


def apply_cpu_clock(current_temperature):
    global CURRENT_CLOCK

    CURRENT_CLOCK = CURRENT_CLOCK + get_clock_percentage_diff(current_temperature)

    if CURRENT_CLOCK < MIN_CLOCK_PCT:
        CURRENT_CLOCK = MIN_CLOCK_PCT
    elif CURRENT_CLOCK > MAX_CLOCK_PCT:
        CURRENT_CLOCK = MAX_CLOCK_PCT

    write_clock_speed_to_file(CURRENT_CLOCK)


def write_clock_speed_to_file(clock_pct):
    with open(MAX_CLOCK_PCT_FILE, 'w') as f:
        f.write(str(clock_pct))


def apply_fan_speed(current_temperature):
    if current_temperature > TARGET_TEMPERATURE - 5:
        level = 64  # unhinged mode, absolute max speed available
    elif current_temperature > TARGET_TEMPERATURE - 10:
        level = 7  # default max speed
    else:
        level = "auto"  # bios controlled speed

    write_fan_speed_to_file(level)


def write_fan_speed_to_file(fan_speed_level):
    with open(IBM_FAN_FILE, 'wb') as f:
        f.write(str.encode("level " + str(fan_speed_level) + "\n"))


def adjust_clock_speed():
    turbo_state_enabled = int(open(NO_TURBO_STATE_FILE, "r").read(1)) == 0
    current_temperature = get_package_temp()

    if turbo_state_enabled:
        apply_cpu_clock(current_temperature)

    if FAN_CONTROL_ENABLED:
        apply_fan_speed(current_temperature)


def start_thermal_daemon():
    start_time = time.time()
    while True:
        adjust_clock_speed()
        time.sleep(RUN_CYCLE_LENGTH_IN_SECONDS - ((time.time() - start_time) % RUN_CYCLE_LENGTH_IN_SECONDS))


if __name__ == '__main__':
    start_thermal_daemon()
