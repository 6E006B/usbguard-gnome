import dbus
from dbus.mainloop.glib import DBusGMainLoop
from enum import IntEnum

from device import Device


class Rule(IntEnum):
    ALLOW = 0
    BLOCK = 1
    REJECT = 2


class USBGuardDBUS(object):

    INSTANCE = None

    @classmethod
    def get_instance(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = USBGuardDBUS()
        return cls.INSTANCE

    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        policy_object = self.bus.get_object('org.usbguard', '/org/usbguard/Policy')
        self.policy_interface = dbus.Interface(policy_object, dbus_interface='org.usbguard.Policy')
        devices_object = self.bus.get_object('org.usbguard', '/org/usbguard/Devices')
        self.devices_interface = dbus.Interface(devices_object, dbus_interface='org.usbguard.Devices')
        self.add_signal_receivers()
        self.device_policy_changed_callbacks = []

    def add_signal_receivers(self):
        self.devices_interface.connect_to_signal('DevicePolicyChanged', self.on_device_policy_changed)

    def on_device_policy_changed(self, id, target_old, target_new, device_rule, rule_id, attributes):
        print("DevicePolicyChanged: {}".format(attributes))
        new_device = Device.generate_device([id, device_rule])
        for callback in self.device_policy_changed_callbacks:
            callback(new_device, rule_id)

    def register_device_policy_changed_callback(self, callback):
        self.device_policy_changed_callbacks.append(callback)

    def unregister_device_policy_changed_callback(self, callback):
        self.device_policy_changed_callbacks.remove(callback)

    def get_all_devices(self):
        devices = self.devices_interface.listDevices('match')
        devices_list = []
        for device in devices:
            devices_list.append(Device.generate_device(device))
        print(repr(devices_list))
        return devices_list

    def get_all_rules(self):
        rules = self.policy_interface.listRules("")
        for rule in rules:
            print(repr(rule))
        return rules

    def apply_device_policy(self, device_id, rule, permanent):
        assert(isinstance(rule, Rule))
        rule_id = self.devices_interface.applyDevicePolicy(device_id, rule, permanent)
        return rule_id

if __name__ == "__main__":
    usbgdbus = USBGuardDBUS()
    usbgdbus.get_all_rules()
    usbgdbus.get_all_devices()