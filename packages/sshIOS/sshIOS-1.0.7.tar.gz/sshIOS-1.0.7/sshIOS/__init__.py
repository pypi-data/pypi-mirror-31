#!/usr/bin/env python3
import sys, socket, getpass
from netmiko import ConnectHandler, NetMikoAuthenticationException

def sshHost(hostname):
    '''Cisco IOS ssh module based on netmiko. Example: "python3 sshHostModuleIOS.py mydevice.lab"'''
    username = input("Username: ")
    password = getpass.getpass()
    hostIp = socket.gethostbyname(hostname)
    try:
        sshSession = ConnectHandler(device_type='cisco_ios', ip=hostIp, username=username, password=password)
    except NetMikoAuthenticationException:
        print('Authentication failed! Please retry')
        sys.exit(1)
    except ValueError:
        print('Enable password wrong! Please retry')
        sys.exit(1)
    else:
        versionHostname = sshSession.send_command("sh running-config | i hostname")
        print('Session established with Hostname: {} IP: {}'.format(versionHostname.replace("hostname ","").strip(), hostIp))
        return sshSession

if __name__ == "__main__":
    try:
        sshHost(sys.argv[1])
    except IndexError:
        print('Please, specify hostname device. Example: "python3 sshHostModuleIOS.py mydevice.lab"')
