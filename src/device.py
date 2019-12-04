# -*- coding: utf8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from rule_parser import RULE


class Device(object):
    """Device class"""

    # TODO: Create more specific lookup also including sub-class and protocol
    # (c.f. http://www.usb.org/developers/defined_class)
    DEVICE_CLASSES = {
        0x00: "Device Unspecified",
        0x01: "Audio (Speaker, microphone, sound card, MIDI)",
        0x02: "Communications and CDC Control (Modem, Ethernet adapter, Wi-Fi adapter, RS232 serial adapter)",
        0x03: "Human Interface Device (HID)",
        0x05: "Physical Interface Device (PID)",
        0x06: "Image(PTP / MTP) (Webcam, scanner)",
        0x07: "Printer",
        0x08: "Mass storage",
        0x09: "USB hub",
        0x0A: "CDC - Data",
        0x0B: "Smart Card",
        0x0D: "Content Security (e.g. Fingerprint reader)",
        0x0E: "Video (e.g. Webcam)",
        0x0F: "Personal healthcare device class (PHDC) (e.g. Pulse monitor (watch))",
        0x10: "Audio / Video (AV)",
        0x11: "Billboard (Describes USB-C alternate modes supported by device)",
        0x12: "USB Type-C Bridge Class",
        0xDC: "Diagnostic Device (USB compliance testing device)",
        0xE0: "Wireless Controller",
        0xEF: "Miscellaneous (ActiveSync device)",
        0xFE: "Application-specific (IrDA Bridge, Test & Measurement Class (USBTMC), USB DFU (Device Firmware Upgrade))",
        0xFF: "Vendor-specific",
    }

    def __init__(self, number, rule, id, serial, name, hash, parent_hash, via_port, with_interface, with_connect_type):
        """Init the class

        number: USBGuard device number
        rule: USBGuard device rule
        id: Vendor/Device ID (04f2:b2ea)
        serial:
        name: Type description of the device ("Integrated Camera")
        hash: USBGuard Hash of the device
        parent_hash: USBGuard parent hash of the device
        via_port: usb port it is connected to
        with_interface: device interface ("type of device" Class:Subclass:Protocol)
        """

        self.number = number
        self.rule = rule
        self.id = id
        self.serial = serial
        self.name = name
        self.hash = hash
        self.parent_hash = parent_hash
        self.via_port = via_port
        self.with_interface = with_interface
        if not isinstance(self.with_interface, list):
            self.with_interface = [self.with_interface]
        self.with_connect_type = with_connect_type

    def has_interface(self, interface_class):
        """

        interface_class: interface class to test for
        returns: true if interface class is supported
        """

        for interface in self.with_interface:
            base_class_bytes = int(interface[:2], 16)
            if base_class_bytes == interface_class:
                return True
        return False

    def is_hid_only(self):
        """Return True if device is HID"""
        for interface in self.with_interface:
            base_class_bytes = int(interface[:2], 16)
            if not base_class_bytes == 0x03:
                return False

        return self.has_interface(0x03)

    def get_class_description_set(self):
        """Get class description based on interface"""
        descriptions = set()
        for interface in self.with_interface:
            base_class_bytes = int(interface[:2], 16)
            descriptions.add(self.DEVICE_CLASSES[base_class_bytes])
        return descriptions

    def get_class_description_string(self):
        """Return the class description string"""
        return "\n".join(self.get_class_description_set())

    def get_interfaces(self):
        """Get device interface id number ("type of device")"""
        return set(self.with_interface)

    def is_allowed(self):
        """Return True if device is allowed"""
        return self.rule.lower() == "allow"

    def get_vendor_id(self):
        """Return vendor id (or None if it cannot be derived from the device id)"""
        return self.id.split(':').get(0, None)

    def get_product_id(self):
        """Return product id (or None if it cannot be derived from the device id)"""
        return self.id.split(':').get(1, None)

    def __str__(self):
        """Return string description of device: number, id, name, rule, class description string"""
        return "<{} ({}) '{}' {} '{}'>".format(self.number, self.id, self.name, self.rule, self.get_class_description_string())

    def __repr__(self):
        return self.__str__()

    def as_list(self):
        """Return device parameter as list (for the GUI grid)"""
        return [
            self.number,
            self.rule == 'allow',
            self.id,
            self.serial,
            self.name,
            self.via_port,
            "\n".join(self.get_interfaces()),
            self.get_class_description_string(),
            self.with_connect_type,
        ]

    # NOTICE: The number is explicitly not part of the comparison here. This
    # is needed for the screensaver new device comparison so upon reinserting
    # the same device does not show in multiple entries.
    def __eq__(self, other):
        """Check if a device equals the current object"""
        print("__eq__()")
        equal = False
        if isinstance(other, Device):
            if (
                    # self.number == other.number and
                    self.rule == other.rule and
                    self.id == other.id and
                    self.name == other.name and
                    self.hash == other.hash and
                    self.parent_hash == other.parent_hash and
                    self.via_port == other.via_port and
                    self.with_interface == other.with_interface and
                    self.with_connect_type == other.with_connect_type
            ):
                equal = True
        return equal

    def __ne__(self, other):
        """Check if another devices does not equal the current object"""
        return not self.__eq__(other)

    def __hash__(self):
        """Return generated device hash identifying the device"""
        print("__hash__()")
        return (
            # hash(self.number) ^
            hash(self.rule) ^
            hash(self.id) ^
            hash(self.name) ^
            hash(self.hash) ^
            hash(self.parent_hash) ^
            hash(self.via_port) ^
            hash(tuple(self.with_interface)) ^
            hash(self.with_connect_type)
        )

    @staticmethod
    def generate_device(device_dbus_struct):
        """Generate a device based on DBus info structure

        device_dbus_struct: Info structure to generate device from
        returns: Device object
        """
        number = int(device_dbus_struct[0])
        info = parse_rule(str(device_dbus_struct[1]))
        return Device(number=number, **info)


def parse_rule(rule_string):
    """Parse a rule

    rule_string: The string of the rule
    returns: a dict
    """
    result_dict = {}
    parsed_rule = RULE.parseString(rule_string).asList()
    result_dict['rule'] = parsed_rule[0]
    for key, value in parsed_rule[1]:
        result_dict[key.replace('-', '_')] = value
    return result_dict


if __name__ == "__main__":
    """Test rule parsing"""
    print(parse_rule('allow id 1d6b:0002 serial "0000:00:14.0" name "xHCI Host Controller" hash "Miigb8mx72Z0q6L+YMai0mDZSlYC8qiSMctoUjByF2o=" parent-hash "G1ehGQdrl3dJ9HvW9w2HdC//pk87pKzFE1WY25bq8k4=" with-interface 09:00:00'))
