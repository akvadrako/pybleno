from distutils.core import setup
setup(
  name = 'pybleno',
  packages = [
      'pybleno',
      'pybleno/examples',
      'pybleno/hci_socket',
      'pybleno/hci_socket/BluetoothHCI',
  ],
  entry_points={
    'console_scripts': [
        'pybleno-magicblue = pybleno.examples.magicblue:main',
    ],
  },
  version = '0.13',
  description = 'A direct port of the Bleno bluetooth LE peripheral role library to Python2/3 (akvadrako fork)',
  author = 'Adam Langley',
  author_email = 'github.com@irisdesign.co.nz',
  url = 'https://github.com/Adam-Langley/pybleno',
  keywords = ['Bluetooth', 'Bluetooth Smart', 'BLE', 'Bluetooth Low Energy'],
  classifiers=[
      'Programming Language :: Python :: 3.7'
  ]
)
