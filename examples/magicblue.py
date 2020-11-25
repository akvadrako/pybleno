#!/usr/bin/env python3
"""
MagicBlue Peripheral Implementation

pip install pybleno
"""

from pybleno import Characteristic, Bleno, BlenoPrimaryService, Descriptor
import signal, array, struct, sys, traceback, os
import codecs

DEVICE_NAME = 'LEDBLE-78628F99'

os.environ['BLENO_DEVICE_NAME'] = DEVICE_NAME
bleno = Bleno()

class RGBChar(Characteristic):
    def __init__(self, uuid):
        super().__init__({
            'uuid': uuid,
            'properties': ['write', 'writeWithoutResponse'],
            'value': None
        })
          
        self._value = array.array('B', [0] * 0)
 
    def onReadRequest(self, offset, callback):
        # Turn on: cc2333
        # Turn off: cc2433
        # 56 RR GG BB 00 f0 aa
        # 56 00 00 00 WW 0f aa
        # bb II (mode = 25 - 38) SS (speed, 1/200ms) 44

        callback(Characteristic.RESULT_SUCCESS, self._value[offset:])

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data
        print('RGB - onWriteRequest', tohex(data), repr(data))
        
        # report device type
        if tohex(data) == 'ef0177':
            #               66    on                temp
            notify(fromhex('66 15 23 4a4102ff111100 0a 99'))
            # 0x66
            # val on = array[2] == 35
            # val temp = array[9].toUInt()

        # report device time
        if tohex(data) == '121a1b21':
            # 0x13 array.size == 11
            #               13 ?  y  m  d  h  m  s  d  ?  31
            notify(fromhex('13 14 14 0b 11 10 38 0c 02 00 31'))
            #    val year = 2000 + array[2].toUInt()
            #    val month = array[3].toUInt()
            #    val day = array[4].toUInt()
            #    val hour = array[5].toUInt()
            #    val minute = array[6].toUInt()
            #    val second = array[7].toUInt()
            #    val dayOfWeek = array[8].toUInt()
        
        callback(Characteristic.RESULT_SUCCESS)

def fromhex(b: str) -> bytes:
    return codecs.decode(b.replace(' ', '').encode(), 'hex')

def tohex(b: bytes) -> str:
    return codecs.encode(b, 'hex').decode()

def notify(msg):
    print('notify', tohex(msg), repr(msg))
    notify_me[0](array.array('B', msg))

notify_me = [None]

class Notify(Characteristic):
    def __init__(self, uuid):
        super().__init__({
            'uuid': uuid,
            'properties': ['notify'],
            'value': None,
            'descriptors': [
               # Descriptor({
               #     'uuid': '2902',
               #     'value': 'Notifications and indications disabled/enabled'
               # }),
            ]
        })
          
    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('Notify - onSubscribe')
        self._updateValueCallback = updateValueCallback
        notify_me[0] = updateValueCallback

    def onUnsubscribe(self):
        print('Notify - onUnsubscribe')
        self._updateValueCallback = None

services = [
    # empty
    BlenoPrimaryService({
        'uuid': 'fff0',
        'characteristics': []
    }),
    
    # rgb
    BlenoPrimaryService({
        'uuid': 'ffe5',
        'characteristics': [ 
            RGBChar('ffe9')
        ]
    }),

    # notify
    BlenoPrimaryService({
        'uuid': 'ffe0',
        'characteristics': [
            Notify('ffe4'),
        ]
    }),
]

def onStateChange(state):
    print('on -> stateChange: ' + state)

    if state == 'poweredOn':
        bleno.startAdvertising(DEVICE_NAME, [s['uuid'] for s in services])
    else:
        bleno.stopAdvertising()

def onAdvertisingStart(error):
    print('on -> advertisingStart: ' + ('error ' + str(error) if error else 'success'))
    bleno.setServices(services)

bleno.on('stateChange', onStateChange)
bleno.on('advertisingStart', onAdvertisingStart)
bleno.start()

import time
time.sleep(3600)

bleno.stopAdvertising()
bleno.disconnect()

