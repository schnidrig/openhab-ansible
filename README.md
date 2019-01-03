# openhab-ansible
Ansible playbooks to setup openhab on a raspberry pi. It'll install mosquitto and mqttwarn as well. Mqttwarn is configured to send data to graphite.

## Prepare Raspberry Pi

### Install raspian

Download it from [https://www.raspberrypi.org/downloads/raspbian/](https://www.raspberrypi.org/downloads/raspbian/)

Unzip and copy it onto an sdcard

e.g on a mac with sdcard reader that would be:

    sudo dd bs=1m if=2016-09-23-raspbian-jessie-lite.img of=/dev/rdiskXYZ


mount sdcard and create an empty file `ssh` at the top level directory. 

Eject card and then insert sdcard into rasberry pi and boot.
    
### Configure fixed ip address

Edit the file `/etc/dhcpcd.conf` and add the following lines (according to your network) and reboot.

    interface eth0
    static ip_address=192.168.1.7/24
    static routers=192.168.1.1
    static domain_name_servers=192.168.1.1

### User setup

- Change password of user pi.
- Install ssh public key for user pi

## memory split

    sudo raspi-config

Then from the advanced menu, change the memory split for the GPU to "16"
restart.

## Run ansible playbook

Edit group_vars/all/vault.
Check/change other values in group_vars

ansible-playbook -i inventory raspi.yml

## performance tweaks

https://github.com/openhab/openhab/wiki/Hardware-FAQ

# install docker
https://www.raspberrypi.org/blog/docker-comes-to-raspberry-pi/
curl -sSL https://get.docker.com | sh


