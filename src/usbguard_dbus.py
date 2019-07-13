# -*- coding: utf8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from enum import IntEnum

from device import Device


class Rule(IntEnum):
    ALLOW = 0
    BLOCK = 1
    REJECT = 2


class PresenceEvent(IntEnum):
    PRESENT = 0
    INSERT = 1
    UPDATE = 2
    REMOVE = 3


class USBGuardDBUS(object):
    """DBUS connect to USBGuard"""

    INSTANCE = None

    @classmethod
    def get_instance(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = USBGuardDBUS()
        return cls.INSTANCE

    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()

        devices_object = self.bus.get_object('org.usbguard', '/org/usbguard/Devices')
        policy_object = self.bus.get_object('org.usbguard', '/org/usbguard/Policy')
        self.policy_interface = dbus.Interface(policy_object, dbus_interface='org.usbguard.Policy')
        self.devices_interface = dbus.Interface(devices_object, dbus_interface='org.usbguard.Devices')

        self.add_signal_receivers()
        self.device_presence_changed_callbacks = []

    def add_signal_receivers(self):
        """Connect to DBUS signals"""
        # TODO: make method private if possible
        self.devices_interface.connect_to_signal('DevicePresenceChanged', self.on_device_presence_changed)

    def on_device_presence_changed(self, id, event, target, device_rule, attributes):
        """Central callback to call back the registered callbacks

        id: USBGuard ID of the device
        event: Event string ('DevicePresenceChanged')
        target: not used
        device_rule: USBGuard device info struct
        attributes: not used
        """
        # TODO: make method private if possible

        new_device = Device.generate_device([id, device_rule])
        for callback in self.device_presence_changed_callbacks:
            callback(event, new_device)

    def register_device_presence_changed_callback(self, callback):
        """Add a callback function to the notification list

        callback: The callback to register
        """
        self.device_presence_changed_callbacks.append(callback)

    def unregister_device_presence_changed_callback(self, callback):
        """Remove a callback function from the notification list

        callback: The callback to unregister
        """
        self.device_presence_changed_callbacks.remove(callback)

    def get_all_devices(self):
        """Return a list of attached devices"""
        devices = self.devices_interface.listDevices('match')
        devices_list = []
        for device in devices:
            devices_list.append(Device.generate_device(device))
        print(repr(devices_list))
        return devices_list

    def get_device(self, device_number):
        """Get details for a specific device

        device_number: Number of device to query
        """
        device = None
        devices = self.devices_interface.listDevices('match')
        for device_struct in devices:
            if int(device_struct[0]) == int(device_number):
                device = Device.generate_device(device_struct)
        return device

    def get_all_rules(self):
        """Return a list of rules"""
        rules = self.policy_interface.listRules("")
        for rule in rules:
            print(repr(rule))
        return rules

    def apply_device_policy(self, device_id, rule, permanent):
        """allow or block a device

        device_id: Device id of the device to authorize.
        rule: Device authorization target as Enum. ALLOW, BLOCK, REJECT.
        permanent: A boolean flag specifying whether an allow rule should be appended to the policy.

        returns: The id of the rule
        """

        assert(isinstance(rule, Rule))
        rule_id = self.devices_interface.applyDevicePolicy(device_id, rule, permanent)
        return rule_id

    def check_device_activated(self, device):
        updated_device = self.get_device(device.number)
        return updated_device.is_allowed()

    def check_devices_activated(self, device_list):
        for device in device_list:
            if not self.check_device_activated(device):
                return False
        return True


if __name__ == "__main__":
    """Test it by getting rules and devices. Prints them"""
    usbgdbus = USBGuardDBUS()
    usbgdbus.get_all_rules()
    usbgdbus.get_all_devices()
