# openhab-ansible
Ansible playbooks to setup openhab on a raspberry pi.

## Prepare Raspberry Pi
### Install raspian
Using the [Raspberry Pi Imager](https://www.raspberrypi.org/software/) install the latest (buster) version.

Mount sd-card and create an empty file `ssh` at the top level directory. 

Eject card and then insert sdcard into rasberry pi and boot.
### Optional: Configure fixed ip address

Edit the file `/etc/dhcpcd.conf` and add the following lines (according to your network) and reboot.

    interface eth0
    static ip_address=192.168.1.7/24
    static routers=192.168.1.1
    static domain_name_servers=192.168.1.1

### User setup

- Install /home/pi/.ssh/authorized_keys for user pi
- delete password for user pi: `passwd --delete pi`

### Dist Upgrade

Upgrade all packages to newest version: 

    apt update
    apt dist-upgrade -y

## Run ansible playbook

first install some galaxy roles:

    ansible-galaxy collection install community.general
    ansible-galaxy collection install community.docker

Edit group_vars/all/vault.
Edit inventory.
Check/change other values in group_vars

ansible-playbook -i inventory raspi.yml

## performance tweaks

https://github.com/openhab/openhab/wiki/Hardware-FAQ

## Logging Config

add the following to /home/pi/userdata/etc/log4j2.xml

                <!-- jython file appender -->
                <RollingRandomAccessFile fileName="${sys:openhab.logdir}/jython.log" filePattern="${sys:openhab.logdir}/jython.log.%i" name="JYTHON">
                        <PatternLayout pattern="%d{yyyy-MM-dd HH:mm:ss.SSS} [%-5.5p] [%-36.36c] - %m%n"/>
                        <Policies>
                                <OnStartupTriggeringPolicy/>
                                <SizeBasedTriggeringPolicy size="8 MB"/>
                        </Policies>
                </RollingRandomAccessFile>

                <Logger additivity="false" level="INFO" name="jython">
                        <AppenderRef ref="JYTHON"/>
                </Logger>

