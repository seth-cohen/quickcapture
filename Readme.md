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
## Then need to copy the global libraries to the virtual env
- cp -r /usr/lib/python3/dist-packages/PyQt5 Venvs/qc/lib/python3.5/site-packages/PyQt5
- cp /usr/lib/python3/dist-packages/sip.cpython-*.so ~/Venvs/qc/lib/python3.5/site-packages
## To interface with the camera
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
## Test install
- Running the program
  - First enable the virtual environment.
  ```
  $ source ~/Venvs/qc/bin/activate
  ```
  
  - Run the program from within the directory
  ```
  $ python3 quickcapture.py
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