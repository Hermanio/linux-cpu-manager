#!/usr/bin/env python3
import sys

import dbus, dbus.service, dbus.exceptions
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from controller import BetterThermalDaemon

# Initialize a main loop
DBusGMainLoop(set_as_default=True)
loop = GLib.MainLoop()

# Declare a name where our service can be reached
try:
    bus_name = dbus.service.BusName("ee.ounapuu.BetterThermalDaemon",
                                    bus=dbus.SystemBus(),
                                    do_not_queue=True)
except dbus.exceptions.NameExistsException:
    print("service is already running")
    sys.exit(1)

# Run the loop
try:
    BetterThermalDaemon(bus_name)
    loop.run()
except KeyboardInterrupt:
    print("keyboard interrupt received")
except Exception as e:
    print("Unexpected exception occurred: '{}'".format(str(e)))
finally:
    loop.quit()
