#!/usr/bin/env bash

sudo cp ./conf/ee.ounapuu.LinuxCPUManager.conf /etc/dbus-1/system.d/

sudo mkdir -p /usr/bin/linux-cpu-manager
sudo cp -a ./src/. /usr/bin/linux-cpu-manager/
sudo chmod +x /usr/bin/linux-cpu-manager/client
sudo chmod +x /usr/bin/linux-cpu-manager/service

sudo cp ./conf/linux-cpu-manager.service /etc/systemd/system/
sudo systemctl enable linux-cpu-manager.service