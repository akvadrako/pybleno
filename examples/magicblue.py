#!/usr/bin/env python3
"""
MagicBlue Peripheral Implementation

For an example client implementation see:
https://github.com/Betree/magicblue


pip install pybleno
"""

from pybleno import Characteristic, Bleno, BlenoPrimaryService, Descriptor
import signal, array, sys, traceback, os
import time
from struct import pack
import codecs
from urllib.request import urlopen

DEVICE_NAME = 'LEDBLE-78628F99'

os.environ['BLENO_DEVICE_NAME'] = DEVICE_NAME
bleno = Bleno()

def switch(name, state):
    print('SWITCH', name, state)
    try:
        print('RESULT', urlopen(f'http://{name}.local/{state}', timeout=3).read().decode())
    except Exception as e:
        print('ERROR', e)

class RGBChar(Characteristic):
    def __init__(self, uuid):
        super().__init__({
            'uuid': uuid,
            'properties': ['write', 'writeWithoutResponse'],
            'value': None
        })
        self.on = False
 
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        print('RGB - onWriteRequest', tohex(data), repr(data))
        
        if tohex(data) == 'cc2333':
            self.on = True
            switch('uitje', 'on')
            switch('onion', 'on')
        
        if tohex(data) == 'cc2433':
            self.on = False
            switch('uitje', 'off')
            switch('onion', 'off')
        
        # 56 00 00 00 WW 0f aa
        if data[0] == 0x56 and data[5] == 0x0f:
            print('WHITE', data[4])
        
        # 56 RR GG BB 00 f0 aa
        if data[0] == 0x56 and data[5] == 0xf0:
            print('RGB', data[1], data[2], data[3])
        
        # bb II (mode = 25 - 38) SS (speed, 1/200ms) 44
        if data[0] == 0xbb:
            print('EFFECT', data[1], data[2])

        # report device type
        if tohex(data) == 'ef0177':
            print('TYPE', self.on)
            notify(pack('12B',
                0x66,
                0x15,
                0x23 if self.on else 0x00,
                0x4a,  # effect no
                0x41,  # effect
                0x02,  # speed
                0xff,  # red
                0x11,  # green
                0x11,  # blue
                0x00,  # white
                10,    # version
                0x99,  # temp?
            ))

        # report device time
        if tohex(data) == '121a1b21':
            print('TIME')
            notify(pack('11B',
                0x13,
                0x14,
                0,  # year - 2000
                1,  # month (1-12)
                1,  # day
                0,  # hour
                0,  # minute
                0,  # second
                1,  # weekday
                0,
                0x31,
            ))
        
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
            'descriptors': [],
        })
          
    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('Notify - onSubscribe')
        notify_me[0] = updateValueCallback

    def onUnsubscribe(self):
        print('Notify - onUnsubscribe')

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

while True:
    time.sleep(60)

bleno.stopAdvertising()
bleno.disconnect()

