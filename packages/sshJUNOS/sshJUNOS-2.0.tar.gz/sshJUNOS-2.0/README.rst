python3/python2 SSH module for session management for multivendor network devices (Juniper, Cisco IOS, Cisco ASA, Arista). Based on Netmiko

``sshJUNOS`` provides a ready-to-go ssh module, asking for ``Username``, ``Password`` and ``Enable Password``.
Error handling and promt information are also provided to facilitate the user in case of wrong username or password.

All `netmiko <https://pynet.twb-tech.com/blog/automation/netmiko.html>`_ commands are available with this module

Example::

  #!/usr/bin/env python3
  import sys
  from sshJUNOS import sshHost as ssh

  def showVersion(host):
      out = host.send_command("show version")
      print(out)

  showVersion(ssh(sys.argv[1]))

How to run it::

  federico@federico:~/git/github/python/modules/python3 $ python3 importTest.py srx00.sw11.lab
  Username: root
  Password:
  Session established with Hostname: Hostname: srx00.sw11.lab IP: 192.168.1.1

  Hostname: srx00.sw11.lab
  Model: srx300
  Junos: 15.1X49-D120.3
  JUNOS Software Release [15.1X49-D120.3]
  [...]
