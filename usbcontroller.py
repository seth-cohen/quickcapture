"""
The ethernet chip is on the usb bus. There are conflicts when
the four cameras and ethernet are all connected

This module was created to control the USB port enabling and disabling

Python 3

@author:    Seth Cohen <scohen@wayfair.com>
@copyright: 2018 Wayfair LLC - All rights reserved
"""
import consts
import subprocess
import configparser

def turn_ethernet_on():
    """Bind the ethernet port and unbind the camera hub port

    """
    ethernet_port, camera_port = get_ports()

    bind_usb_port(camera_port, False)
    bind_usb_port(ethernet_port, True)
        
def turn_ethernet_off():
    """Unbind the ethernet port and bind the camera hub port

    """
    ethernet_port, camera_port = get_ports()
    
    bind_usb_port(ethernet_port, False)
    bind_usb_port(camera_port, True)

def enable_all_usb():
    ethernet_port, camera_port = get_ports()
    
    bind_usb_port(ethernet_port, False)
    bind_usb_port(camera_port, False)
    bind_usb_port(ethernet_port, True)
    bind_usb_port(camera_port, True)
    
def get_ports():
    """Gets the ports from the config file

    Returns:
        tuple: (ethernet_port, camera_port)

    """
    config = configparser.ConfigParser()
    config.read(consts.CONFIG_FILE)

    ethernet_port = config.get('USB', 'ethernet', fallback=consts.DEFAULT_ETHERNET_USB_PORT)
    camera_port = config.get('USB', 'camera_hub', fallback=consts.DEFAULT_CAMERA_HUB_USB_PORT)

    return (ethernet_port, camera_port)

def bind_usb_port(port, should_bind):
    """Binds or unbinds usb ports

    Args:
        port (string): The usb port description that should be (un)bound. 
            (IE. '1-1.1.1' == Bus 1, Port 1 > subport 1 > subport 1
                 '1-1.2' == Bus 1, Port 1 > subport 2)
        should_bind (bool): Whether we want to bind (True) or unbind (False) the port

    """
    try:
        print('Turning {} Port {}'.format('on' if should_bind else 'off', port))
        cmd = 'echo "{}" | sudo tee /sys/bus/usb/drivers/usb/{}bind'.format(
            port,
            '' if should_bind else 'un'
        )
        subprocess.check_output(cmd, shell=True)
        time.sleep(0.2)
    except:
        # swallow the error since this typically means already (un)bound and
        # we don't really care about that
        pass
