import io
import sys
import gphoto2 as gp
import camerafactory as cf
import gpiocontroller as gpio


class CameraTrigger():
    # keep track if we initialized GPIOs yet. if not then init from trigger
    is_gpio_init = False

    def __init__(self, gpio_pin, trigger_on_low=True):
        self.gpio_pin = int(gpio_pin)
        self.trigger_on_low = trigger_on_low
        self.gpio = gpio.GpioController.get_instance()

        self.gpio.set_pin_mode(self.gpio_pin, gpio.OUTPUT)
        self.turn_off_gpio()
        
    def trigger_on(self, duration):
        direction = gpio.LOW
        if not self.trigger_on_low:
            direction = gpio.HIGH
            
        self.gpio.set_with_duration(self.gpio_pin, direction, duration)
        
    def turn_off_gpio(self):
        direction = gpio.HIGH
        if not self.trigger_on_low:
            direction = gpio.LOW
            
        self.gpio.set_gpio(self.gpio_pin, direction)

class Camera():
    def __init__(self, trigger_pin, serial_num):
        # number of photos that this camera has taken since program start
        self.number_of_photos_taken = 0

        # rPi pin connected to camera to trigger
        self.trigger = CameraTrigger(trigger_pin, True)

        print('Cam on pin {} has serial number {}'.format(trigger_pin, serial_num))
        if not serial_num is None:
            self.camera = cf.CameraFactory.get_instance().get_camera(serial_num)
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
