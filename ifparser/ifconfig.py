from __future__ import unicode_literals, print_function
from .re_scan import ScanEnd, Scanner


class Interface(object):
    _attr_list = (
        'interface', 'itype', 'mtu', 'ip', 'bcast', 'mask', 'hwaddr', 'ptp'
    )
    _cnt_field_list = (
        'txbytes', 'rxbytes', 'rxpkts', 'txpkts',
        'txerrors', 'rxerrors', 'txdroppedpkts', 'rxdroppedpkts',
        'txoverruns', 'rxoverruns', 'txcarrier', 'rxframe'
    )
    _flag_list = (
        'BROADCAST', 'MULTICAST', 'UP', 'RUNNING', 'LOOPBACK', 'DYNAMIC',
        'PROMISC', 'NOARP', 'POINTOPOINT', 'SIMPLEX', 'SMART', 'MASTER',
        'SLAVE'
    )

    _attrs = frozenset(_attr_list)
    _cnt_fields = frozenset(_cnt_field_list)
    _flags = frozenset(_flag_list)
    _non_flags = _attrs.union(_cnt_fields)
    _all_fields = _non_flags.union(_flags)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, name):
        """
        Return False if flag not set
        """
        if name in Interface._non_flags:
            return None
        if name in Interface._flags:
            return False

    def __setattr__(self, name, value):
        if name in Interface._all_fields:
            if value is not None:
                super(Interface, self).__setattr__(name, value)
        else:
            raise ValueError("Invalid attribute mentioned name=%s value=%s" %
                             (name, value))

    def __str__(self):
        return "%s-%s" % ("obj", self.interface)

    def __repr__(self):
        return self.__str__()

    def get_values(self):
        value_dict = {}
        for attr in Interface._all_fields:
            value_dict[attr] = getattr(self, attr)
        return value_dict


class ParseError(Exception):
    pass


class InterfaceNotFound(Exception):
    pass


class Ifcfg(object):
    scanner = Scanner([
        ('process_interface',
         r"(?P<interface>^[a-zA-Z0-9:._-]+)\s+"
         r"Link encap\:(?P<itype>[A-Za-z0-9-]+(?: [A-Za-z0-9-]+)*)\s*"
         r"(?:HWaddr(?:\s(?P<hwaddr>[0-9A-Fa-f:-]*)))?.*"),
        ('process_any', r"\s+ether\s(?P<hwaddr>[0-9A-Fa-f:]+).*"),
        ('process_ip', r"\s+inet[\s:].*"),
        ('process_mtu', r"\s+(?P<states>[A-Z\s]+\s*)+MTU:(?P<mtu>[0-9]+).*"),
        ('process_any', r"\s+RX bytes:(?P<rxbytes>\d+).*?"
         r"TX bytes:(?P<txbytes>\d+).*"),
        ('process_any',
         r"\s+RX packets[:\s](?P<rxpkts>\d+)"
         r"\s+errors[:\s](?P<rxerrors>\d+)"
         r"\s+dropped[:\s](?P<rxdroppedpkts>\d+)"
         r"\s+overruns[:\s](?P<rxoverruns>\d+)"
         r"\s+frame[:\s](?P<rxframe>\d+)"
         ".*"),
        ('process_any',
         r"\s+TX packets[:\s](?P<txpkts>\d+)"
         r"\s+errors[:\s](?P<txerrors>\d+)"
         r"\s+dropped[:\s](?P<txdroppedpkts>\d+)"
         r"\s+overruns[:\s](?P<txoverruns>\d+)"
         r"\s+carrier[:\s](?P<txcarrier>\d+)"
         r".*"),
        ('process_interface2',
         r"(?P<interface>^[a-zA-Z0-9-]+).*?<(?P<states>[A-Z,]+\s*)>"
         r".*?mtu (?P<mtu>[0-9]+).*"),
        ('process_ignore', r"(Ifconfig|Infiniband|Because)\s.*"),
        ('process_ignore', r"\s+.*"),
    ])

    def __init__(self, raw_text, debug=False):
        self.debug = debug
        self._interfaces = {}
        self.curr_interface = None
        lines = raw_text if isinstance(raw_text, list) else \
            raw_text.splitlines()
        self._process(lines)

    def _process(self, lines):
        for line in lines:
            try:
                for token, match in Ifcfg.scanner.scan(line):
                    process_func = getattr(self, token)
                    process_func(match.groups(),
                                 match.groupdict(), match.group())
            except ScanEnd:
                raise ParseError(repr(line))

    def set_curr_interface_attr(self, kwargs):
        for k, v in kwargs.items():
            if v is not None:
                setattr(self._interfaces[self.curr_interface], k, v)

    def process_interface(self, group, groupdict, matched_str):
        self.curr_interface = groupdict['interface']
        self._interfaces[self.curr_interface] = Interface()
        self.set_curr_interface_attr(groupdict)

    def process_interface2(self, group, groupdict, matched_str):
        self.curr_interface = groupdict['interface']
        self._interfaces[self.curr_interface] = Interface()
        states = groupdict.pop('states').strip().split(',')
        for st in states:
            groupdict[st] = True
        self.set_curr_interface_attr(groupdict)

    def process_ip(self, group, groupdict, matched_str):
        if ':' in matched_str:
            splitattrs = (matched_str.strip()
                          .lower()
                          .replace('inet addr', 'ip')
                          .replace('p-t-p', 'ptp')
                          .split())
            for attr in splitattrs:
                name, value = attr.split(':')
                setattr(self._interfaces[self.curr_interface], name, value)
        else:
            map_dict = {'inet': 'ip', 'netmask': 'mask', 'broadcast': 'bcast'}
            kv = iter(matched_str.split())
            for k, v in zip(kv, kv):
                groupdict[map_dict[k]] = v
            self.set_curr_interface_attr(groupdict)

    def process_any(self, group, groupdict, matched_str):
        self.set_curr_interface_attr(groupdict)

    def process_mtu(self, group, groupdict, matched_str):
        states = groupdict.pop('states').strip().split()
        for st in states:
            groupdict[st] = True
        self.set_curr_interface_attr(groupdict)

    def process_ignore(self, group, groupdict, matched_str):
        if self.debug:
            print("{0} {1} {2}".format(group, groupdict, matched_str))

    @property
    def interfaces(self):
        return sorted(self._interfaces.keys())

    def get_interface(self, interface):
        if interface in self._interfaces:
            return self._interfaces[interface]
        raise InterfaceNotFound(
            "No such interface {0} found.".format(interface))

    def get(self, **kwargs):
        for key in kwargs.keys():
            key_check = key in Interface._all_fields
            if not key_check:
                raise ValueError("Invalid argument: %s" % key)
        eligible = []
        for name, interface in self._interfaces.items():
            inc_check = True
            for key in kwargs.keys():
                if not inc_check:
                    continue
                inc_check = getattr(interface, key) == kwargs[key]
            if inc_check:
                eligible.append(interface)
        return eligible
