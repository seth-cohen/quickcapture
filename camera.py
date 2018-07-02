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
        
    def turn_off_gpio(self):
        direction = gpio.HIGH
        if not self.trigger_gpio_low:
            direction = gpio.LOW
            
        self.gpio.set_gpio(self.gpio_pin, direction)

class Camera():
    def __init__(self, trigger_pin, serial_num, position, completed_callback=None, trigger_with_usb=False):
        # number of photos that this camera has taken since program start
        self.number_of_photos_taken = 0

        # rPi pin connected to camera to trigger
        self.trigger = CameraTrigger(trigger_pin, True)
        self.trigger_with_usb = trigger_with_usb

        # Position of the camera, 0 being top camera
        self.position = position

        print('Cam on pin {} has serial number {}'.format(trigger_pin, serial_num))
        if not serial_num is None:
            self.camera = cf.CameraFactory.get_instance().get_camera(serial_num)

            # Debugging
            if self.camera is not None:
                camera_config = self.camera.get_config()
                child_count = camera_config.count_children()
                if child_count < 1:
                    return
                tabs = None
                for child in camera_config.get_children():
                    label = '{} ({})'.format(child.get_label(), child.get_name())
                    child_type = child.get_type()
                    print(label)
        else:
            self.camera = None

        self.files = {}
        self.file_save_callback = completed_callback
        self.thread = None
            
    async def take_photo(self, container=None):
        """Takes the actual photo

        Triggers the camera either via USB or gpio pins
        Args:
            container (str): The key that we want to associate the image with 
                typically the name of the scan or 'initialization'

        """
        if self.camera is None:
            return

        while self.thread is not None:
            await asyncio.sleep(0.2)
            
        if container is None:
            container = 'inititalization'

        if not self.trigger_with_usb:
            self.trigger.trigger_on(0.5)
        else:
            self.camera.trigger_capture()

        if self.thread is None:
            print('====== Creating Thread for cam {} ======'.format(self.position))
            self.thread = CameraEventThread(self.camera, 5.0, container)
            self.thread.file_name_signal.connect(self.handle_image_save)
            self.thread.daemon = True
            self.thread.start()
    
    def get_preview(self, file, folder):
        # if self.camera is None:
        #     print('No Camera attached')
        #     return None
        # 
        # print('Capturing preview image')
        # camera_file = self.camera.capture_preview()
        # file_data = camera_file.get_data_and_size()
        # return file_data
        print(folder, file)
        try:
            print('====== Capturing Preview for cam {} ======'.format(self.position))
            exif = self.camera.file_get(folder, file, gp.GP_FILE_TYPE_PREVIEW)
            return exif.get_data_and_size()
        except Exception as e:
            print(e)
            
        return None

    def get_file_info(self, path):
        folder, name = os.path.split(path)
        print(folder, name)
        return  self.camera.file_get_info(folder, name)

    def handle_image_save(self, file, directory, container):
        print('--- === Image save callback === ---')
        if container not in self.files:
            self.files[container] = []

        if len(file) > 0 and len(directory) > 0:
            self.files[container].append(os.path.join(directory, file))

            if self.file_save_callback is not None:
                self.file_save_callback(self.position, file, directory)

        self.thread = None
        
    def list_files(self, path='/'):
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
            result.extend(self.list_files(os.path.join(path, name)))

        return result

class CameraEventThread(Qtc.QThread):
    """Waits for events to be registered from the camera

    Useful so we can fire and forget and still get alerted when images
    are actually saved to disk

    """
    file_name_signal = Qtc.pyqtSignal(str, str, str)
    def __init__(self, camera, wait_time, container=None):
        super().__init__()
        self.camera = camera
        self.wait_time = wait_time
        self.container = container

    def run(self):
        start = time.time()
        file_name = ''
        folder = ''
        while time.time() - start < self.wait_time:
            event = self.camera.wait_for_event(200)
            if event[0] == gp.GP_EVENT_FILE_ADDED:
                print('====== file_saved ======')
                file_path_details = event[1]
                file_name = file_path_details.name
                folder = file_path_details.folder
                break
        
        self.file_name_signal.emit(
            file_name,
            folder,
            self.container
        )
