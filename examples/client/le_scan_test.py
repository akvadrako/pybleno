#!/usr/bin/python
from signal import pause
import struct
from pybleno.hci_socket.BluetoothHCI import BluetoothHCI
from pybleno.hci_socket.BluetoothHCI.constants import *
from pybleno.hci_socket.constants2 import *

# based on: https://github.com/sandeepmistry/node-bluetooth-hci-socket/blob/master/examples/le-scan-test.js


class BluetoothLEScanTest:

    def __init__(self, dev_id=0):
        self.hci = BluetoothHCI(dev_id, auto_start=False)
        self.hci.on_data(self.on_data)
        self.hci.on_started(self.on_started)
        print(self.hci.get_device_info())
        self.found_bd_addrs = set()
        self.hci.start()

    def on_started(self):
        print('started')
        self.set_scan_enable(False)
        self.set_filter()
        # reset?
        self.set_scan_parameters()
        self.set_scan_enable(True, True)

    def __del__(self):
        print('deleted')
        self.hci.on_data(None)
        self.hci.stop()


    def set_filter(self):
        typeMask   = 1 << HCI_EVENT_PKT
        eventMask1 = (1 << EVT_CMD_COMPLETE) | (1 << EVT_CMD_STATUS)
        eventMask2 = 1 << (EVT_LE_META_EVENT - 32)
        opcode     = 0

        filter = struct.pack("<LLLH", typeMask, eventMask1, eventMask2, opcode)
        self.hci.set_filter(filter)

    def set_scan_parameters(self):
        len = 7
        type = SCAN_TYPE_ACTIVE
        internal = 0x0010   #  ms * 1.6
        window = 0x0010     #  ms * 1.6
        own_addr  = LE_PUBLIC_ADDRESS
        filter = FILTER_POLICY_NO_WHITELIST
        cmd = struct.pack("<BHBBHHBB", HCI_COMMAND_PKT, LE_SET_SCAN_PARAMETERS_CMD, len,
                          type, internal, window, own_addr, filter )

        self.hci.write(cmd)


    def set_scan_enable(self, enabled=False, duplicates=False):
        len = 2
        enable = 0x01 if enabled else 0x00
        dups   = 0x01 if duplicates else 0x00
        cmd = struct.pack("<BHBBB", HCI_COMMAND_PKT, LE_SET_SCAN_ENABLE_CMD, len, enable, dups)
        self.hci.write(cmd)


    def on_data(self, data):
        if data[0] == HCI_EVENT_PKT:
            print("HCI_EVENT_PKT")
            if data[1] == EVT_CMD_COMPLETE:
                print("EVT_CMD_COMPLETE")
                # TODO: unpack based on: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/hci.h#n1853

                if (data[5]<<8) + data[4] == LE_SET_SCAN_PARAMETERS_CMD:
                    if data[6] == HCI_SUCCESS:
                        print('LE Scan Parameters Set');

                elif data[5]<<8 + data[4] ==  LE_SET_SCAN_ENABLE_CMD:
                    if data[6] == HCI_SUCCESS:
                        print('LE Scan Enable Set')

            elif data[1] == EVT_LE_META_EVENT:
                print("EVT_LE_META_EVENT")
                if data[3] == EVT_LE_ADVERTISING_REPORT:

                    # TODO: unpack based on: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/hci.h#n2167

                    gap_adv_type =['ADV_IND', 'ADV_DIRECT_IND', 'ADV_SCAN_IND', 'ADV_NONCONN_IND', 'SCAN_RSP'][data[5]]
                    gap_addr_type = ['PUBLIC', 'RANDOM'][data[6]]
                    gap_addr =  [hex(c) for c in data[12:6:-1]]

                    gap_addr_str =  ':'.join([hex(c) for c in data[12:6:-1]])
                    self.found_bd_addrs.add(gap_addr_str)
                    eir = [chr(c) for c in data[14:-2]]
                    rssi = data[-1]

                    print('LE Advertising Report')
                    print('\tAdv Type  = {}'.format(gap_adv_type))
                    print('\tAddr Type = {}'.format(gap_addr_type))
                    print('\tAddr      = {}'.format(gap_addr_str))
                    print('\tEIR       = {}'.format(eir))
                    print('\tRSSI      = {}'.format(rssi))

if __name__ == '__main__':
    ble_scan_test = BluetoothLEScanTest()
    import time
    while True:
        time.sleep(1)
    print(ble_scan_test)
