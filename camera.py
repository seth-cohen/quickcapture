import os
import io
import gphoto2 as gp
import camerafactory as cf
import gpiocontroller as gpio
import collections as col


class CameraTrigger():
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
    def __init__(self, trigger_pin, serial_num, position):
        # number of photos that this camera has taken since program start
        self.number_of_photos_taken = 0

        # rPi pin connected to camera to trigger
        self.trigger = CameraTrigger(trigger_pin, True)

        # Position of the camera, 0 being top camera
        self.position = position

        print('Cam on pin {} has serial number {}'.format(trigger_pin, serial_num))
        if not serial_num is None:
            self.camera = cf.CameraFactory.get_instance().get_camera(serial_num)
        else:
            self.camera = None

        self.files = []
        if self.camera is not None:
            self.files.extend(self.list_files())
            
    def take_photo(self):
        if self.camera is None:
            return
        
        self.number_of_photos_taken += 1
        self.trigger.trigger_on(0.5)

    def get_new_photo(self):
        diff = list(set(self.files) - set(self.files[:-1]))
        if len(diff) > 0:
            return diff[0]
        else:
            return ''
    
    def get_preview(self):
        if self.camera is None:
            print('No Camera attached')
            return None
        
        print('Capturing preview image')
        camera_file = self.camera.capture_preview()
        file_data = camera_file.get_data_and_size()
        return file_data

    def get_file_info(self, path):
        folder, name = os.path.split(path)
        return  self.camera.file_get_info(folder, name)

    def list_files(self, path='/'):
        result = []
        # get files
        for name, value in self.camera.folder_list_files(path):
            result.append(os.path.join(path, name))
        # read folders
        folders = []
        for name, value in self.camera.folder_list_folders(path):
            folders.append(name)
        # recurse over subfolders
        for name in folders:
            result.extend(self.list_files(os.path.join(path, name)))

        return result
