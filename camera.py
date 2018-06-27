import wiringpi as wpi
import threading
import time
import io
import sys
import gphoto2 as gp
from camerafactory import CameraFactory


class CameraTrigger():
    # keep track if we initialized GPIOs yet. if not then init from trigger
    is_gpio_init = False

    def __init__(self, gpio_pin, trigger_on_low=True):
        self.gpio_pin = int(gpio_pin)
        self.trigger_on_low = trigger_on_low

        # set the pin to output so we can pull high/low and trigger
        if not CameraTrigger.is_gpio_init:
            wpi.wiringPiSetup()
            CameraTrigger.is_gpio_init = True

        wpi.pinMode(self.gpio_pin, wpi.OUTPUT)
        self.turn_off_gpio()
        
    def trigger_on(self, duration):
        direction = wpi.LOW
        if not self.trigger_on_low:
            direction = wpi.HIGH
            
        self.set_gpio_with_duration(direction, duration)

    def set_gpio_with_duration(self, direction, duration):
        self.set_gpio(direction)

        next_direction = CameraTrigger.toggle_direction(direction)
        print('Triggering Thread for Pin {} setting to {} in {} sec'.format(self.gpio_pin, next_direction, duration) )
        threading.Timer(duration, self.set_gpio, args=(next_direction,)).start()

    def set_gpio(self, direction):
        print('Setting Pin {} {}'.format(self.gpio_pin, direction))
        wpi.digitalWrite(self.gpio_pin, direction)
        
    def turn_off_gpio(self):
        direction = wpi.HIGH
        if not self.trigger_on_low:
            direction = wpi.LOW
            
        self.set_gpio(direction)

    def toggle_direction(direction):
        if direction == wpi.HIGH:
            return wpi.LOW
        else:
            return wpi.HIGH
        
class Camera():
    def __init__(self, trigger_pin, serial_num):
        # number of photos that this camera has taken since program start
        self.number_of_photos_taken = 0

        # rPi pin connected to camera to trigger
        self.trigger = CameraTrigger(trigger_pin, True)

        if not serial_num is None:
            self.camera = CameraFactory.get_instance().get_camera(serial_num)
        else:
            self.camera = None
            
    def take_photo(self):
        self.number_of_photos_taken += 1
        self.trigger.trigger_on(0.5)

    def get_preview(self):
        if self.camera is None:
            print('No Camera attached')
            return None
        
        print('Capturing preview image')
        camera_file = gp.check_result(gp.gp_camera_capture_preview(self.camera))
        file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
        return file_data
