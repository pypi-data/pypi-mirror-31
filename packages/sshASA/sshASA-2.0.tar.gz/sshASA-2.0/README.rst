python3/python2 SSH module for ssh session management for multivendor network devices (Juniper, Cisco IOS, Cisco ASA, Arista).
This module is entirely based on Netmiko

``sshASA`` provides a ready-to-go ssh module, asking for ``Username``, ``Password`` and ``Enable Password``.
Error handling and promt information are also provided to facilitate the user in case of wrong username or password

All `netmiko <https://pynet.twb-tech.com/blog/automation/netmiko.html>`_ commands are available with this module

Example::

  #!/usr/bin/env python3
  import sys
  from sshASA import sshHost as ssh

  def showVersion(host):
      out = host.send_command("show version")
      print(out)

  showVersion(ssh(sys.argv[1]))

How to run it::

  federico@federico:~/git/github/python/modules/python3 $ python3 importTest.py FIREWALL01
  Username: olivierif
  Password:
  Enable password:
  Session established with Hostname:FIREWALL01 IP:10.10.10.93

  Cisco Adaptive Security Appliance Software Version 9.1(7)23
  Device Manager Version 7.5(2)153
  [...]
