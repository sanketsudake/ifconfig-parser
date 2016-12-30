ifconfig-parser
################

Parse ifconfig output collected from local or remote server and retrieve required
interface information.

Usage
=====
Install ifconfig-parser:

.. code-block:: bash

    pip install -U ifparser

You can access inferface information as below :

.. code-block:: python

    >>> import commands
    >>> from ifparser import Ifcfg
    >>> ifdata = Ifcfg(commands.getoutput('ifconfig -a'))
    >>> ifdata.interfaces
    ['lo', 'docker0', 'eth0']
    >>> eth0 = ifdata.get_interface('eth0')
    >>> eth0.BROADCAST
    True
    >>> eth0.hwaddr, eth0.mtu, eth0.ip, eth0.UP
    ('08:00:27:1f:d8:b0', '1500', '10.0.2.15', True)


You can query for intefaces on particular parameter :

.. code-block:: python

    >>> ifdata.get(itype='Ethernet')
    [obj-docker0, obj-eth0]
    >>> ifdata.get(UP=True)
   [obj-lo, obj-docker0, obj-eth0]

Get all interface parameters with ``get_values``. Following dictionary contains all possible values:

.. code-block:: python

    >>> eth0 = ifdata.get_interface('eth0')
    >>> eth0.get_values()
    {'BROADCAST': True,
     'LOOPBACK': False,
     'MULTICAST': True,
     'RUNNING': True,
     'UP': True,
     'bcast': '10.10.2.255',
     'hwaddr': 'FF:FF:27:1f:d8:b0',
     'interface': 'eth0',
     'ip': '10.10.2.15',
     'itype': 'Ethernet',
     'mask': '255.255.255.0',
     'mtu': '1500',
     'rxbytes': '547873',
     'rxpkts': '628',
     'txbytes': '50826',
     'txpkts': '424'}

List of parameters for interface:

- BROADCAST, LOOPBACK, MULTICAST, RUNNING, UP, DYNAMIC
- interface - Interface name, itype - Interface Type
- ip - IP, bcast - Broadcast, mask - Mask
- hwaddr - MAC address, mtu - MTU
- rxbytes - Received Bytes, rxpkts - Received Packets
- txbytes - Sent Bytes, txpkts - Sent Packets
