# This gets the Qt stuff
import sys
import PyQt5
import PyQt5.QtWidgets as Qtw
import PyQt5.QtGui as Qtg
import PyQt5.QtCore as Qtc
import wiringpi as wpi
import pathlib

# facilitate asynchronous operations
import os
import time
import asyncio

# styling
import qdarkstyle

import configparser
import camera
import consts
import turntable

# This is our window from QtCreator
import mainwindow_auto as main
import dialogs.configdialog as configdialog
import dialogs.ftpdialog as ftpdialog
import dialogs.newscandialog as scandialog
import dialogs.messagedialog as msgdialog


# create class for our Raspberry Pi GUI
class MainWindow(Qtw.QMainWindow, main.Ui_MainWindow):
    """MainWindow is the top level GUI window running in the main thread

    This QT5 QMainWindow offers functionality consisting of viewing image previews, 
    initiating scans or setup shots, and transfering data to the processing FTP servers

    Attributes:
        scans (dict of str: [ScanDetails]): Dictionary of scans key is name of scan and value is the scan details for each part
            tuple where first index is number of series and second is a string of notes/description of scan 
        scan_name (str): Name of the current scan
        scan_part_count (int): Current part number of the current scan
        image_associations ([ImageAssociation]): List of ImageAssociations, mapping an image to the scan and photo type
        config (ConfigParser): Object to read and right application configuration
    
    """
    
    def __init__(self):
        """Initializes all variables and state for the application and sets up the UI

        """
        super().__init__()
        self.setupUi(self) # gets defined in the UI file
        self.connect_ui()

        self.scans = {}
        self.scan_name = ''
        self.scan_part_count = 1
        self.base_dir = os.path.join(str(pathlib.Path.home()), time.strftime('%Y%m%d'))

        self.image_associations = []

        self.config = configparser.ConfigParser()
        self.config.read(consts.CONFIG_FILE)
        # if we don't already have a config file we should generate one
        if len(self.config.sections()) == 0:
            print('No Config file present')
            self.generate_default_config()
            self.display_config()

        self.setup_hardware()
        self.refresh_camera_settings()
        self.reset_previews()
        
    def setup_hardware(self):
        self.cameras = [];
        for x in range(0, 4):
            self.cameras.append(
                camera.Camera(
                    self.config['DEFAULTS']['camera{}pin'.format(x + 1)],
                    self.config['CAMERAS'].get('camera{}serial'.format(x + 1), None),
                    x
                )
            )

        turntable_data = self.config['TURNTABLE']
        self.turntable = turntable.Turntable(
            int(turntable_data.get('turntablepin', consts.DEFAULT_TURNTABLE_PIN)),
            int(turntable_data.get('timetorotate', consts.DEFAULT_TURNTABLE_PERIOD)),
            int(turntable_data.get('photosperscan', consts.DEFAULT_PHOTOS_PER_SCAN)),
            float(turntable_data.get('delay', consts.DEFAULT_DELAY))
        )
        
    def connect_ui(self):
        self.cam_counters = []
        self.cam_previews = []
        self.cam_settings = []
        for i in range(1, 5):
            self.cam_counters.append(getattr(self, 'image_count_{}'.format(i)))
            self.cam_previews.append(getattr(self, 'thumbnail_{}'.format(i)))
            self.cam_settings.append({
                'aperture': getattr(self, 'aperture_{}'.format(i)),
                'shutter': getattr(self, 'shutter_{}'.format(i)),
                'focus': getattr(self, 'focus_mode_{}'.format(i)),
                'iso': getattr(self, 'ISO_{}'.format(i)),
                'shoot': getattr(self, 'shoot_mode_{}'.format(i)),
                'lens': getattr(self, 'lens_{}'.format(i)),
                'counter': getattr(self, 'counter_{}'.format(i)),
                'available': getattr(self, 'available_{}'.format(i))
            })
        
        self.initialize_button.clicked.connect(self.initialization_shot)
        self.new_scan_button.clicked.connect(self.start_scan)
        self.ftp_button.clicked.connect(self.display_ftp)
        self.actionClose.triggered.connect(self.close)
        self.actionConfig.triggered.connect(self.display_config)

        self.scan_progress_container.hide()
        self.scan_progress.setValue(0)

    def refresh_camera_settings(self):
        for cam_num, camera in enumerate(self.cameras):
           self.cam_settings[cam_num]['aperture'].setText(camera.aperture)
           self.cam_settings[cam_num]['shutter'].setText(camera.shutter_speed)
           self.cam_settings[cam_num]['focus'].setText(camera.focus_mode)
           self.cam_settings[cam_num]['iso'].setText(camera.ISO)
           self.cam_settings[cam_num]['shoot'].setText(camera.shoot_mode)
           self.cam_settings[cam_num]['lens'].setText(camera.lens)
           self.cam_settings[cam_num]['counter'].setText(camera.counter)
           self.cam_settings[cam_num]['available'].setText(camera.available)
           
    def reset_previews(self):
        """Place camera preview placeholder in place of the live feeds
        
        """
        path = os.path.dirname(os.path.abspath(__file__))
        preview_image_path = os.path.join(path, 'cam_no_preview.png')
        for preview in self.cam_previews:
            preview.setPixmap(Qtg.QPixmap(preview_image_path).scaled(preview.width(), preview.height(), Qtc.Qt.KeepAspectRatio))

    def generate_default_config(self):
        """Sets the known defaults for the config file.
        
        If there is no pre-generated config file at ~/.quickcapture.conf this method
        should be called prior to completing initialization so that we can generate 
        the config file with appropriate default values

        """
        self.config['DEFAULTS'] = {
            'camera1pin': consts.DEFAULT_CAM_1_PIN,
            'camera2pin': consts.DEFAULT_CAM_2_PIN,
            'camera3pin': consts.DEFAULT_CAM_3_PIN,
            'camera4pin': consts.DEFAULT_CAM_4_PIN
        }
        self.config['TURNTABLE'] = {
            'timetorotate': consts.DEFAULT_TURNTABLE_PERIOD,
            'photosperscan': consts.DEFAULT_PHOTOS_PER_SCAN,
            'turntablepin': consts.DEFAULT_TURNTABLE_PIN,
            'delay': consts.DEFAULT_DELAY
        }
        self.config['FTP'] = {
            'Host': 'FTPPartner.wayfair.com'
        }
        
    def display_config(self):
        init = configdialog.ConfigDialog(self.config)
        # We want a modal dialog. exec_() will open the dialog Modally.
        if init.exec_():
            self.config = init.config
            self.update_config()
            self.reset_previews()
            self.setup_hardware()
            self.refresh_camera_settings()

    def display_ftp(self):
        ftp = ftpdialog.FTPDialog(self.config, self.cameras, self.image_associations, self.scans, self.base_dir)
        if ftp.exec():
            # reset camera counts etc.            
            pass
        
    def close(self):
        exit()
        
    def start_scan(self):
        """Kicks off the scan processEvents

        Display dialog to enter details about the scan then starts the process of rotating
        the turntable and capturing photos from all attached cameras.

        """
        dialog = scandialog.NewScanDialog(len(self.scans) == 0, self.scan_name)
        if dialog.exec_():
            self.scan_progress_container.show()
            
            scan_name = dialog.scan_name
            scan_notes = dialog.scan_notes
            scan_type = dialog.scan_type
            if dialog.is_additional_part:
                self.scan_part_count += 1
            else:
                self.scan_part_count = 1

            if self.scan_part_count > 1:
                self.scan_name_label.setText('{} (Part {})'.format(scan_name, self.scan_part_count))
                self.scans[scan_name].append(ScanDetails(1, scan_type, scan_notes))
            else:
                self.scan_name_label.setText(scan_name)
                self.scans[scan_name] = [ScanDetails(1, scan_type, scan_notes)]

            self.scan_name = scan_name
            self.perform_scan_cycle()

            orientation_image = Qtg.QPixmap()
            orientation_image.load('orientation.png')
            while self.show_message_box(
                'Start Scan Cycle',
                'New Orientation',
                'Would you like to shoot an additional orientation of this part?',
                ('If you would like to shoot a new orientation of this same part'
                 ' place it on it\'s side, adjust and refocus cameras. Then click `Start Scan Cycle` button'),
                orientation_image,
                True
            ):
                self.scans[scan_name][self.scan_part_count - 1].num_series += 1
                self.perform_scan_cycle()

    def waiting_on_previews(self):
        for cam in self.cameras:
            if cam.thread is not None:
                return True

        return False
            
    def update_scan_progress(self, current_scan):
        total_scans = self.turntable.photos_per_scan + 2
        self.total_scan_label.setText(str(total_scans))
        self.current_scan_label.setText(str(current_scan))
        self.scan_progress.setValue(100 * current_scan / total_scans)
        
    def perform_scan_cycle(self):
        cam_list = range(len(self.cameras))
        print('~===-*^% Photos per scan {}'.format(self.turntable.photos_per_scan))

        self.update_scan_progress(0)
        for shot in range(self.turntable.photos_per_scan):
            print('=============== LOOPING ================')
            if shot > 0:
                self.turntable.rotate_slice()
            self.take_photo_for_cams(cam_list, True, 'scan')

            self.update_scan_progress(shot + 1)
            # Ensure that the GUI updates to show the new preview
            for i in range(10):
                time.sleep(0.01)
                Qtw.QApplication.processEvents()


        Qtw.QApplication.processEvents()
        background_image = Qtg.QPixmap()
        background_image.load('background.png')
        self.show_message_box(
            'Take Photo',
            'Background Shot',
            'Take a photo of the empty stage for a background shot',
            'Remove object and then click the `Take Photo` button to shoot the empty stage and background',
            background_image
        )
        self.take_photo_for_cams(cam_list, True, 'background')
        self.update_scan_progress(self.turntable.photos_per_scan + 1)

        Qtw.QApplication.processEvents()
        checker_image = Qtg.QPixmap()
        checker_image.load('colorcard.png')
        self.show_message_box(
            'Take Photo',
            'Color Checker',
            'Take photo of the stage with the color checker',
            'Ensure color checker is visible in each camera of the cameras and the click `Take Photo` button',
            checker_image
        )
        self.take_photo_for_cams(cam_list, True, 'colorcard')
        self.update_scan_progress(self.turntable.photos_per_scan + 2)
        print(self.scans)

    def show_message_box(self, button_text, title, text, informative_text=None, image=None, is_choice=False):
        msgbox = msgdialog.MessageDialog(
            button_text,
            title,
            text,
            informative_text,
            image,
            is_choice
        )
        return msgbox.exec_()
        
    def take_photo_for_cams(self, which_cams, for_scan=False, type=None):
        # Name the bucket that we want to associate these images with
        association = 'initialization'
        series = None
        if for_scan:
            series = self.scans[self.scan_name][self.scan_part_count - 1].num_series
            full_scan_name = self.scan_name
            if self.scan_part_count > 1:
                full_scan_name += '-{}of'.format(self.scan_part_count)
            association = full_scan_name

        coroutines = []
        for cam_num in which_cams:
            coroutines.append(self.cameras[cam_num].take_photo(association))
            
        loop = asyncio.get_event_loop()
        responses = loop.run_until_complete(asyncio.gather(*coroutines))

        for i, cam_num in enumerate(which_cams):
            response = responses[i]

            # if response is not none then the camera shot succeeded
            if response is not None and len(response) > 0:
                cam = self.cameras[cam_num]
                self.cam_counters[cam_num].display(cam.number_of_photos_taken)
                self.textEdit.append('Cam {}: {}'.format(cam_num + 1, response['file']))
                cam.load_config_settings()
                self.refresh_camera_settings()

                self.image_associations.append(ImageAssociation(
                    response['file'],
                    cam_num,
                    association,
                    series,
                    type
                ))
                    
                # Grab the thumbnail of the image to display, this way we can get an
                # idea for the quality.
                # @TODO see if we can get something higher quality than the thumbnail
                preview = cam.get_preview(response['file'], response['dir'])
                if preview is not None:
                    preview_pixmap = Qtg.QPixmap()
                    preview_pixmap.loadFromData(preview)

                    thumbnail = self.cam_previews[cam_num]
                    thumbnail.setPixmap(preview_pixmap.scaled(thumbnail.width(), thumbnail.height(), Qtc.Qt.KeepAspectRatio))
            

    def initialization_shot(self):
        print('============ Taking initialization shots ===============')
        self.take_photo_for_cams(range(len(self.cameras)))

    def update_config(self):
        """This method is called any time our configuration has changed

        We need to update the application's conf file and also apply the configuration 
        changes to ensure proper operation.

        """
        print('Updating Config File')
        with open(consts.CONFIG_FILE, 'w+') as config_file:
            self.config.write(config_file)

    def toggle_pin(self, pinsoreview):
        if wpi.digitalRead(pin) == 1:
            wpi.digitalWrite(pin, 0)
        else:
            wpi.digitalWrite(pin, 1)

class ImageAssociation():
    def __init__(self, file_path, camera, scan_name, series, image_type):
        self.camera_number = camera
        self.scan_name = scan_name
        self.series = series
        self.image_type = image_type
        self.file_path = file_path

    def __repr__(self):
        xstr = lambda v: '' if v is None else v
        return '{}, {}, {}, {}, {}\n'.format(self.file_path, xstr(self.scan_name), xstr(self.series), self.camera_number, xstr(self.image_type))

class ScanDetails():
    def __init__(self, num_series, type, notes):
        self.num_series = num_series
        self.type = type
        self.notes = notes

    def __repr__(self):
        return '{}, {}, "{}"'.format(self.num_series, self.type, self.notes)
        
# I feel better having one of these
def main():
    # a new app instance
    consts.app = Qtw.QApplication(sys.argv)
    consts.app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    form = MainWindow()
    form.show()
    
    # without this, the script exits immediately.
    sys.exit(consts.app.exec_())
 
# python bit to figure how who started This
if __name__ == "__main__":
    main()
