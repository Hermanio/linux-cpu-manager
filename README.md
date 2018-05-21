# linux-cpu-manager
Linux CPU manager is a service that allows the user to control CPU performance modes via included governors and prevent overheating with the included pre-emptive throttling functionality. 

Work in progress.


## How to run
This service is guaranteed to run on a fresh installation of Ubuntu 18.04. It may run on other recent distributions, too, such as Arch Linux, but at this point others have not been tested. 

1. Make sure that `thermald` is not running and in a disabled state as it conflicts with the CPU manager. Run
`sudo systemctl disable thermald.service` 
and
`sudo systemctl stop thermald.service`
to make sure that it is not running.

2. To deploy the dbus config file, run
`sudo bash deploy-dbus-conf.sh`

3. Start the service with 
`sudo python3 src/btd-service`. The service should be running with debug output in the console.

4. To change the governor, run `python3 src/btd-client 'governor-name-here'`. Example of setting the governor to powersave mode:
`python3 src/btd-client powersave`


