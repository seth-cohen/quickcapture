## Pinout and connections
- connector pins 2 and 4 for 5v power for relays.
- connector pin 6 for ground
- connector pin 22 (wiring pi pin 6) turntable
- connector pin 24 (wirint pi pin 10) for camera 1 (top)
- connector pin 26 (wirint pi pin 11) for camera 2 (top-middle)
- connector pin 28 (wirint pi pin 31) for camera 3 (bottom-middle)
- connector pin 32 (wirint pi pin 26) for camera 4 (bottom)

## Install virtual env
- pip install virtual env
- python3 -m venv ~/Venvs/qc
## Install python qt5 for the PI:
- sudo apt-get install python3-pyqt5
  - Otherwise you'll have to build it and sip which will be a pain on 
    a Pi
## Install wiring pi
- First activate the Venv
  ```
  $ source ~/Venvs/qc/bin/activate
  ```
- pip install wiringpi
## We are going to be dealing with user passwords so we'll want to encrypt and decrypt
- pip install pycryptodome
## Then need to copy the global libraries to the virtual env
- cp -r /usr/lib/python3/dist-packages/PyQt5 Venvs/qc/lib/python3.5/site-packages/PyQt5
- cp /usr/lib/python3/dist-packages/sip.cpython-*.so ~/Venvs/qc/lib/python3.5/site-packages
## To interface with the camera over USB. This is not for the faint of heart... the documentation
is not great for this with python but I found the source code [here][python-gphoto2] and there is
a way to play with it and see what calls you need to make
- Install gphoto2
  ```
  $ sudo apt-get install gphoto2
  ```
  That will give you command line interface.
- Then we want it for python too. Get the dev package so we can build it ourselves
  ```
  sudo apt-get install libgphoto2-dev
  ```
- install the python wrapper - This takes a while (do it in the venv)
  ```
  pip install -v gphoto2
  ```
- if we want to access images we need pillow installed
  ```
  pip install pillow
  ```
- There is an annoyance with the gvfs Gnome file system that will auto mount the camera when connected.
This is a prblem because then gphoto2, in some firmware versions, will not be able to claim the device
  - To prevent this you must update the file system explorer
  Add the following to `~/.config/pcmanfm/LXDE-pi/pcmanfm.conf`
  ```
  [volume]
  mount_on_startup=0
  mount_removable=0
  ```
## Styling
- pip install qdarkstyle
-

## Test install
- Running the program
  - First enable the virtual environment.
  ```
  $ source ~/Venvs/qc/bin/activate
  ```
  
  - Run the program from within the directory
  ```
  $ python3 wayscan.py
  ```
## On Mac
- install QtCreator 
  - download from https://www.qt.io/download-qt-installer?hsCtaTracking=9f6a2170-a938-42df-a8e2-a9f0b1d6cdce%7C6cb0de4f-9bb5-4778-ab02-bfb62735f3e5

## Support
- https://pinout.xyz/pinout/pin22_gpio25

## Wireless access point for networking
- https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

## Bluetooth file transfer
- use obexpushd, need to update /etc/systemd/system/dbus-org.bluez.service

## Get rid of annoying a11y warning
- sudo apt-get install at-spi2-core

[python-gphoto2]: https://github.com/jim-easterbrook/python-gphoto2/tree/master/src/gphoto2
