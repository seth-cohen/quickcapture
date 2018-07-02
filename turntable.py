import time
import threading
import consts
import gpiocontroller as gpio

class Turntable():
    def __init__(
            self,
            gpio_pin=consts.DEFAULT_TURNTABLE_PIN,
            period=consts.DEFAULT_TURNTABLE_PERIOD,
            photos_per_scan=consts.DEFAULT_PHOTOS_PER_SCAN,
            delay=consts.DEFAULT_DELAY
    ):
        self.period = period
        self.photos_per_scan = photos_per_scan
        self.enable_rotation_duration = self.period / photos_per_scan
        self.delay = delay
        self.gpio_pin = gpio_pin
        self.gpio = gpio.GpioController.get_instance()
        self.gpio.set_pin_mode(self.gpio_pin, gpio.OUTPUT)
        self.gpio.set_gpio(self.gpio_pin, gpio.HIGH)
        self.is_rotating = False
        
    def rotate_slice(self):
        print('Rotating table for {} seconds'.format(self.enable_rotation_duration))
        self.gpio.set_gpio(self.gpio_pin, gpio.LOW)

        # time.sleep(self.enable_rotation_duration)
        # self.gpio.set_gpio(self.gpio_pin, gpio.HIGH)

        self.is_rotating = True
        threading.Timer(self.enable_rotation_duration, self.terminate_rotation)

    def terminate_rotation():
        self.gpio.set_gpio(self.gpio_pin, gpio.HIGH)
        self.is_rotating = False
