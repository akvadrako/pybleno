from pybleno import *
import sys
import signal
from EchoCharacteristic import *

print('bleno - echo')

bleno = Bleno()

def onStateChange(state):
   print('on -> stateChange: ' + state);

   if (state == 'poweredOn'):
     bleno.startAdvertising('echo', ['ec00'])
   else:
     bleno.stopAdvertising();

bleno.on('stateChange', onStateChange)
    
def onAdvertisingStart(error):
    print('on -> advertisingStart: ' + ('error ' + str(error) if error else 'success'));

    if not error:
        bleno.setServices([
            BlenoPrimaryService({
                'uuid': 'ec00',
                'characteristics': [ 
                    EchoCharacteristic('ec0F')
                    ]
            })
        ])
bleno.on('advertisingStart', onAdvertisingStart)

bleno.start()

import time
time.sleep(3600)

bleno.stopAdvertising()
bleno.disconnect()

print ('terminated.')
sys.exit(1)
