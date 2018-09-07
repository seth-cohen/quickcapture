import os
import io
import gphoto2 as gp
import collections as col
import PyQt5.QtCore as Qtc
import time
import asyncio
import camerafactory as cf
import gpiocontroller as gpio


class CameraTrigger():
    def __init__(self, gpio_pin, trigger_gpio_low=True):
        self.gpio_pin = int(gpio_pin)
        self.trigger_gpio_low = trigger_gpio_low
        self.gpio = gpio.GpioController.get_instance()

        self.gpio.set_pin_mode(self.gpio_pin, gpio.OUTPUT)
        self.turn_off_gpio()

    def trigger_on(self, duration):
        direction = gpio.LOW
        if not self.trigger_gpio_low:
            direction = gpio.HIGH
            
        self.gpio.set_with_duration(self.gpio_pin, direction, duration)
        print(direction)
        
    def turn_off_gpio(self):
        direction = gpio.HIGH
        if not self.trigger_gpio_low:
            direction = gpio.LOW
            
        self.gpio.set_gpio(self.gpio_pin, direction)

class Camera():
    def __init__(self, trigger_pin, serial_num, position, trigger_gpio_low=True, trigger_with_usb=False):
        # number of photos that this camera has taken since program start
        self.number_of_photos_taken = 0

        # rPi pin connected to camera to trigger
        self.trigger = CameraTrigger(trigger_pin, trigger_gpio_low)
        self.trigger_with_usb = trigger_with_usb

        # Position of the camera, 0 being top camera
        self.position = position

        self.files = {}
        self.thread = None

        self.aperture = 'N/A'
        self.ISO = 'N/A'
        self.focus_mode = 'N/A'
        self.shutter_speed = 'N/A'
        self.shoot_mode = 'N/A'
        self.counter = 'N/A'
        self.available = 'N/A'
        self.lens = 'N/A'
        self.serial_num = serial_num
        self.model = 'N/A'
        
        print('Cam on pin {} has serial number {}'.format(trigger_pin, serial_num))
        if not serial_num is None:
            self.camera = cf.CameraFactory.get_instance().get_camera(serial_num)
            self.load_config_settings()
        else:
            self.camera = None
            
    def load_config_settings(self):
        if self.camera is not None:
            config = self.camera.get_config()
            
            self.aperture = config.get_child_by_name('aperture').get_value()
            self.ISO = config.get_child_by_name('iso').get_value()
            self.focus_mode = config.get_child_by_name('focusmode').get_value()
            self.shutter_speed = config.get_child_by_name('shutterspeed').get_value()
            self.shoot_mode = config.get_child_by_name('autoexposuremode').get_value()
            self.counter = config.get_child_by_name('shuttercounter').get_value()
            self.available = config.get_child_by_name('availableshots').get_value()
            self.lens = config.get_child_by_name('lensname').get_value()
            self.model = config.get_child_by_name('cameramodel').get_value()
            
    async def take_photo(self, container=None):
        """Takes the actual photo


        Triggers the camera either via USB or gpio pins. This is a coroutine called
        via asyncio, so that multiple cameras can take photos at the same time without being blocked
        returns the folder and name of the photo as saved on the device

        Args:
            container (str): The key that we want to associate the image with 
                typically the name of the scan or 'initialization'

        """
        if self.camera is None:
            return

        if container is None:
            container = 'inititalization'

        if not self.trigger_with_usb:
            print('Triggering cam {}'.format(self.position))
            self.trigger.trigger_on(0.5)
        else:
            self.camera.trigger_capture()

        file_name = None
        folder = None
        while file_name is None:
            file_name, folder = await self.wait_for_event(5.0)

        return self.handle_image_save(file_name, folder, container)

    async def wait_for_event(self, wait_time, event_to_wait=gp.GP_EVENT_FILE_ADDED):
        """Listen for a total of wait_time seconds for a specific event

        Cameras stream out a series of events while performing certain actions. There is a blocking
        call in the libgphoto2 library that can wait for the events to be emitted. This coroutine
        can run asynchronously to listen to events, specifically the file added event to 
        know when images are actually saved.

        """
        start = time.time()
        file_name = ''
        folder = ''
        while time.time() - start < wait_time:
            event = self.camera.wait_for_event(10)
            if event[0] == event_to_wait:
                file_path_details = event[1]
                file_name = file_path_details.name
                folder = file_path_details.folder
                print('\t----==== Cam {} - file_saved {} ====----'.format(self.position, file_name))
                break
            await asyncio.sleep(0.01)

        if file_name is not None and folder is not None:
            self.number_of_photos_taken += 1

        return (file_name, folder)
            
    async def clear_events(self, wait_time=2.0):
        """Clear as many of the events as we can for the specified time

        When connected to the camera events are buffered and only read out when requested.
        This can lead to the file_added event not being called for the latest file but
        instead for a file previously saved

        Call this to ensure that any events that were triggered before we care are discarded
        """
        if self.camera is not None:
            start = time.time()
            while time.time() - start < wait_time:
                event = self.camera.wait_for_event(10)
                if event[0] == gp.GP_EVENT_FILE_ADDED:
                    print('clearing image from {}'.format(self.position))
                await asyncio.sleep(0.01)

        return True

    def get_preview(self, file, folder):
        try:
            print('\t----==== Grabbing Thumbnail for cam {}, file {} ====----'.format(self.position, file))
            start = time.time()
            file = self.camera.file_get(folder, file, gp.GP_FILE_TYPE_PREVIEW)
            data = file.get_data_and_size()
            print('{} seconds to get file data'.format(time.time() - start))
            return data
        except Exception as e:
            print(e)
             
        return None

    def get_lens_preview(self):
        try:
            print('\t----==== Grabbing Preview for cam {} ====----'.format(self.position))
            start = time.time()

            file = self.camera.capture_preview()
            data = file.get_data_and_size()
            print('{} seconds to get file data'.format(time.time() - start))

            config = self.camera.get_config()
            output = config.get_child_by_name('output')
            output.set_value(output.get_choice(3))

            vf = config.get_child_by_name('viewfinder')
            vf.set_value(0)
            self.camera.set_config(config)

            return data
        except Exception as e:
            print(e)

        return None

    def get_file_info(self, path):
        folder, name = os.path.split(path)
        print(folder, name)
        return  self.camera.file_get_info(folder, name)

    def handle_image_save(self, file, directory, container):
        if container not in self.files:
            self.files[container] = []

        save_details = {}
        if len(file) > 0 and len(directory) > 0:
            self.files[container].append(os.path.join(directory, file))
            save_details['file'] = file
            save_details ['dir'] = directory

        return save_details
        
    def list_all_files(self, path='/'):
        result = []
        if self.camera is None:
            return result
        
        # get files
        for name, value in self.camera.folder_list_files(path):
            result.append(os.path.join(path, name))
        # read folders
        folders = []
        for name, value in self.camera.folder_list_folders(path):
            folders.append(name)
        # recurse over subfolders
        for name in folders:
            result.extend(self.list_all_files(os.path.join(path, name)))

        return result

    def list_files(self):
        return [image for images in self.files.values() for image in images]

