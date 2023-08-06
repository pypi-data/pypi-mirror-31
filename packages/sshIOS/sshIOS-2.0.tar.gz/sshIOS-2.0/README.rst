python3/python2 SSH module for session management for multivendor network devices (Juniper, Cisco IOS, Cisco ASA, Arista). Based on Netmiko

``sshIOS`` provides a ready-to-go ssh module, asking for ``Username``, ``Password`` and ``Enable Password``.
Error handling and promt information are also provided to facilitate the user in case of wrong username or password

All `netmiko <https://pynet.twb-tech.com/blog/automation/netmiko.html>`_ commands are available with this module

Example::

  #!/usr/bin/env python3
  import sys
  from sshIOS import sshHost as ssh

  def showVersion(host):
      out = host.send_command("show version")
      print(out)

  showVersion(ssh(sys.argv[1]))

How to run it::

  federico@federico:~/git/github/python/modules/python3 $ python3 importTest.py ios.sw11.lab
  Username: root
  Password:
  Session established with Hostname: Hostname: ios.sw11.lab IP: 192.168.255.50

  Cisco IOS Software, C2600 Software (C2600-ADVIPSERVICESK9-M), Version 12.3(4)T4,  RELEASE SOFTWARE (fc2)
  Technical Support: http://www.cisco.com/techsupport
  Copyright (c) 1986-2004 by Cisco Systems, Inc.
  [...]
