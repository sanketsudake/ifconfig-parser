import unittest

from ifparser import Ifcfg, Interface


class IfcfgTestCase(unittest.TestCase):
    def setUp(self):
        fp = open('tests/iftest.txt', 'r')
        data = fp.read()
        fp.close()
        self.ifparser = Ifcfg(data, debug=True)

    def test_ifcfg_count(self):
        _ifparser = self.ifparser
        self.assertEqual(len(_ifparser.interfaces), 19)

    def test_ifcfg_flags(self):
        _ifparser = self.ifparser
        interface = _ifparser.get_interface('p1p1')
        self.assertIsInstance(interface, Interface)
        self.assertEqual(interface.UP, True)
        self.assertEqual(interface.RUNNING, True)
        self.assertEqual(interface.BROADCAST, True)
        self.assertEqual(interface.MULTICAST, True)
        self.assertEqual(interface.LOOPBACK, False)

        interface = _ifparser.get_interface('lo')
        self.assertIsInstance(interface, Interface)
        self.assertEqual(interface.UP, True)
        self.assertEqual(interface.RUNNING, True)
        self.assertEqual(interface.BROADCAST, False)
        self.assertEqual(interface.MULTICAST, False)
        self.assertEqual(interface.LOOPBACK, True)

    def test_hwaddr(self):
        _ifparser = self.ifparser
        interface = _ifparser.get_interface('vcsbr')
        self.assertEqual(interface.hwaddr, 'FF:FF:FF:72:AA:AF')
        self.assertEqual(interface.ip, '100.100.1.1')
        self.assertEqual(interface.bcast, '100.100.255.255')
        self.assertEqual(interface.mask, '255.255.0.0')
        self.assertEqual(interface.mtu, '1500')
        self.assertEqual(interface.txpkts, '18')
        self.assertEqual(interface.rxpkts, '0')
        self.assertEqual(interface.txbytes, '2717')
        self.assertEqual(interface.rxbytes, '0')


class IfcfgTestCase2(unittest.TestCase):
    def setUp(self):
        fp = open('tests/iftest_2.txt', 'r')
        data = fp.read()
        fp.close()
        self.ifparser = Ifcfg(data, debug=True)

    def test_interfaces(self):
        _ifparser = self.ifparser
        self.assertEqual(len(_ifparser.interfaces), 6)


class IfcfgTestCase3(unittest.TestCase):
    def setUp(self):
        fp = open('tests/iftest_3.txt', 'r')
        data = fp.read()
        fp.close()
        self.ifparser = Ifcfg(data, debug=True)

    def test_interfaces(self):
        _ifparser = self.ifparser
        self.assertEqual(len(_ifparser.interfaces), 3)
        self.assertEqual(_ifparser.interfaces, ['docker0', 'eth0', 'lo'])

    def test_get(self):
        _ifparser = self.ifparser
        self.assertNotEqual(_ifparser.get(interface='lo'), [])
        self.assertNotEqual(_ifparser.get(interface='docker0'), [])
        self.assertNotEqual(_ifparser.get(interface='eth0'), [])
        print(_ifparser.get(UP=True))
        self.assertEqual(
            [
                _ifparser.get(interface='docker0')[0],
                _ifparser.get(interface='eth0')[0],
                _ifparser.get(interface='lo')[0]
            ],
            sorted(_ifparser.get(UP=True)))
        self.assertEqual(
            _ifparser.get(interface='eth0'),
            _ifparser.get(hwaddr='08:00:27:1f:d8:b0'))


class IfcfgTestCaseDynamic(unittest.TestCase):
    def setUp(self):
        fp = open('tests/iftest_4.txt', 'r')
        data = fp.read()
        fp.close()
        self.ifparser = Ifcfg(data, debug=True)

    def test_interfaces(self):
        _ifparser = self.ifparser
        self.assertEqual(len(_ifparser.interfaces), 3)
        self.assertEqual(_ifparser.interfaces, ['eth0', 'lo', 'wlan0'])


class IfcfgTestCase5(unittest.TestCase):
    def setUp(self):
        fp = open('tests/iftest_5.txt', 'r')
        data = fp.read()
        fp.close()
        self.ifparser = Ifcfg(data, debug=True)

    def test_interfaces(self):
        _ifparser = self.ifparser
        self.assertEqual(len(_ifparser.interfaces), 8)
        self.assertEqual(_ifparser.interfaces,
                         ['eth1.60', 'eth1.60:1', 'gre0', 'ip6tnl0', 'lo',
                          'port_100_br0_l', 'rmnetctl', 'sit0'])


class IfcfgTestCase6(unittest.TestCase):
    def setUp(self):
        fp = open('tests/iftest_6.txt', 'r')
        data = fp.read()
        fp.close()
        self.ifparser = Ifcfg(data, debug=True)

    def test_interface_slave_value(self):
        _ifparser = self.ifparser
        self.assertEqual(len(_ifparser.interfaces), 1)
        self.assertEqual(_ifparser.interfaces, ['enp135s0f0'])
        interface = _ifparser.get_interface('enp135s0f0')
        values = interface.get_values()
        self.assertEqual(True, values['SLAVE'])


class IfcfgTestCase7(unittest.TestCase):
    def setUp(self):
        fp = open('tests/iftest_7.txt', 'r')
        data = fp.read()
        fp.close()
        self.ifparser = Ifcfg(data, debug=True)

    def test_interface_slave_value(self):
        _ifparser = self.ifparser
        self.assertEqual(len(_ifparser.interfaces), 1)
        self.assertEqual(_ifparser.interfaces, ['vpn0'])
        interface = _ifparser.get_interface('vpn0')
        self.assertEqual(interface.POINTOPOINT, True)
        self.assertEqual(interface.ptp, '10.0.0.2')
        self.assertEqual(interface.ip, '10.0.0.2')
        values = interface.get_values()
        self.assertEqual(True, values['POINTOPOINT'])
