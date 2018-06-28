import time
import threading
import wiringpi as wpi

OUTPUT = wpi.OUTPUT
HIGH = wpi.HIGH
LOW = wpi.LOW

class GpioController():
    __instance = None

    def get_instance():
        if GpioController.__instance == None:
            GpioController()

        return GpioController.__instance

    def __init__(self):
        if GpioController.__instance != None:
            raise Exception('Do not call GpioController() directly. Use static get_instance')
        else:
            GpioController.__instance = self

        wpi.wiringPiSetup()

    def set_pin_mode(self, pin_num, mode):
        wpi.pinMode(pin_num, mode)

    def toggle_direction(self, direction):
        if direction == HIGH:
            return LOW
        else:
            return HIGH

    def set_gpio(self, pin_num, direction):
        print('Setting Pin {} {}'.format(pin_num, direction))
        wpi.digitalWrite(pin_num, direction)
        
    def set_with_duration(self, pin_num, direction, duration):
        self.set_gpio(pin_num, direction)

        next_direction = self.toggle_direction(direction)
        print('Triggering Thread for Pin {} setting to {} in {} sec'.format(pin_num, next_direction, duration) )
        threading.Timer(duration, self.set_gpio, args=(pin_num, next_direction,)).start()
