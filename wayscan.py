#!/home/pi/Venvs/qc/bin/python
# This gets the Qt stuff
import sys
import PyQt5
import PyQt5.QtWidgets as Qtw
import PyQt5.QtGui as Qtg
import PyQt5.QtCore as Qtc

import wiringpi as wpi
import pathlib
import atexit

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
import usbcontroller

# This is our window from QtCreator
import mainwindow_auto as main
import dialogs.configdialog as configdialog
import dialogs.ftpdialog as ftpdialog
import dialogs.newscandialog as scandialog
import dialogs.messagedialog as msgdialog


THUMBNAIL_TAB_INDEX = 0
CAMERA_SETTINGS_TAB_INDEX = 1


# create class for our Raspberry Pi GUI
class MainWindow(Qtw.QMainWindow, main.Ui_MainWindow):
    """MainWindow is the top level GUI window running in the main thread

    This QT5 QMainWindow offers functionality consisting of viewing image previews,
    initiating scans or setup shots, and transfering data to the processing FTP servers

    Attributes:
        scans (dict of str: [ScanDetails]): Dictionary of scans key is name of scan and value is the scan details for each part
            tuple where first index is number of series and second is a string of notes/description of scan
        scan_name (str): Name of the current scan
        scan_part_id (str): Unique ID of the product being scanned. If a prop or experiment it defaults to scan name
        scan_part_count (int): Current part number of the current scan
        image_associations ([ImageAssociation]): List of ImageAssociations, mapping an image to the scan and photo type
        config (ConfigParser): Object to read and right application configuration

    """

    def __init__(self, splash):
        """Initializes all variables and state for the application and sets up the UI

        """
        super().__init__()
        self.setupUi(self) # gets defined in the UI file
        self.connect_ui()

        self.scans = {}
        self.scan_name = ''
        self.scan_part_id = ''
        self.scan_part_count = 1
        self.base_dir = os.path.join(str(pathlib.Path.home()), time.strftime('%Y%m%d_%H%M%S'))

        self.image_associations = []

        splash.showMessage('Loading Configuration File')
        self.config = configparser.ConfigParser()
        self.config.read(consts.CONFIG_FILE)
        # if we don't already have a config file we should generate one
        if len(self.config.sections()) == 0:
            print('No Config file present')
            splash.showMessage('No Config File Present')
            self.generate_default_config()
            self.display_config()

        splash.showMessage('Setting Up Hardware')
        self.setup_hardware()

        splash.showMessage('Grabbing Camera Settings')
        self.refresh_camera_settings()

        splash.showMessage('Setting Camera Preview Image')
        self.reset_previews()

        # Let's ensure that we have at least 20GB available space
        st = os.statvfs(os.path.expanduser('~'))
        gigs_free = st.f_bavail * st.f_frsize / 1024 / 1024 / 1024

        if gigs_free < 20:
            Qtw.QMessageBox.critical(
                self,
                'Low Free Disk Space',
                ('Please delete old desktop directories '
                 'space is down to {:.2f} GB remaining. '
                 'Open file explorer to "/home/pi/ and delete '
                 'the dated directories only (YYYYMMDD_XXXXXX)'.format(gigs_free))
            )

    def setup_hardware(self):
        self.cameras = [];
        if 'DEFAULTS' in self.config and 'CAMERAS' in self.config:
            for x in range(0, 4):
                self.cameras.append(
                    camera.Camera(
                        self.config['DEFAULTS']['camera{}pin'.format(x + 1)],
                        self.config['CAMERAS'].get('camera{}serial'.format(x + 1), None),
                        x,
                        self.config['DEFAULTS'].getboolean('triggerlow', False)
                    )
                )

        if 'TURNTABLE' in self.config:
            turntable_data = self.config['TURNTABLE']
            self.turntable = turntable.Turntable(
                int(turntable_data.get('turntablepin', consts.DEFAULT_TURNTABLE_PIN)),
                float(turntable_data.get('timetorotate', consts.DEFAULT_TURNTABLE_PERIOD)),
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

            available_text = self.cam_settings[cam_num]['available']
            available_text.setText(camera.available)
            try:
                print(int(camera.available))
                if int(camera.available) < 60:
                    available_text.setStyleSheet('QLabel{color:red; font-weight:bold}')
                else:
                    available_text.setStyleSheet('')
            except ValueError:
                pass

    def reset_previews(self):
        """Place camera preview placeholder in place of the live feeds

        """
        path = os.path.dirname(os.path.abspath(__file__))
        preview_image_path = os.path.join(path, 'cam_no_preview.png')
        for preview in self.cam_previews:
            preview.setPixmap(Qtg.QPixmap(preview_image_path).scaled(preview.width(), preview.height(), Qtc.Qt.KeepAspectRatio))

    def generate_default_config(self):
        """Sets the known defaults for the config file.

        If there is no pre-generated config file at ~/.wayscan.conf this method
        should be called prior to completing initialization so that we can generate
        the config file with appropriate default values

        """
        self.config['DEFAULTS'] = {
            'camera1pin': consts.DEFAULT_CAM_1_PIN,
            'camera2pin': consts.DEFAULT_CAM_2_PIN,
            'camera3pin': consts.DEFAULT_CAM_3_PIN,
            'camera4pin': consts.DEFAULT_CAM_4_PIN,
            'triggerlow': False
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
        self.config['USB'] = {
            'ethernet': consts.DEFAULT_ETHERNET_USB_PORT,
            'camera_hub': consts.DEFAULT_CAMERA_HUB_USB_PORT
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
        print(self.base_dir)
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
        dialog = scandialog.NewScanDialog(
            len(self.scans) == 0,
            self.scan_name,
            self.scan_part_id,
            list(self.scans.keys())
        )
        if dialog.exec_():
            self.create_files_if_necessary()
            self.tabWidget.setCurrentIndex(THUMBNAIL_TAB_INDEX)
            self.scan_progress_container.show()

            scan_name = dialog.scan_name
            scan_part_id = dialog.part_id if dialog.part_id != '' else scan_name
            scan_notes = dialog.scan_notes
            object_type = dialog.object_type
            scan_type = dialog.scan_type
            generate_3d_model = dialog.should_generate_3d_model
            if dialog.is_additional_part:
                self.scan_part_count += 1
            elif dialog.is_additional_orientation:
                # continue where we left off but increment series
                self.scans[scan_part_id][self.scan_part_count - 1].num_series += 1
            else:
                self.scan_part_count = 1

            # if this was an oops moment and we are actually trying to
            # shoot an additional orientation of the previous
            # part then everythin is already set up
            if not dialog.is_additional_orientation:
                if self.scan_part_count > 1:
                    self.scan_name_label.setText('{}{} (Part {})'.format(
                        '[{}]: '.format(scan_part_id) if scan_part_id != scan_name else '',
                        scan_name,
                        self.scan_part_count
                    ))
                    self.scans[scan_part_id].append(ScanDetails(1, scan_type, object_type, scan_notes, scan_name, generate_3d_model))
                else:
                    self.scan_name_label.setText('{}{}'.format(
                        '[{}]: '.format(scan_part_id) if scan_part_id != scan_name else '',
                        scan_name
                    ))
                    self.scans[scan_part_id] = [ScanDetails(1, scan_type, object_type, scan_notes, scan_name, generate_3d_model)]

                self.scan_name = scan_name
                self.scan_part_id = scan_part_id

            self.write_to_scan_details(overwrite_line=dialog.is_additional_orientation)
            # start the scan cycle
            self.perform_scan_cycle()

            Qtw.QApplication.processEvents()
            while self.show_message_box(
                'Start Scan Cycle',
                'New Orientation',
                'Reorient item for additional scan series',
                ('Invert, place on its side or otherwise position the subject'
                 ' to capture additional data. When prepared, select "Start Scan Cycle."'
                 ' When you have scanned all needed orientations select New Part/Item'),
                get_pixmap('orientation.png'),
                True,
                no_button_text='New Part/Item'
            ):
                self.scans[scan_part_id][self.scan_part_count - 1].num_series += 1
                self.write_to_scan_details(overwrite_line=True)
                self.perform_scan_cycle()

    def write_to_scan_details(self, overwrite_line=False):
        """Write the current scan information to the csv file

        Writes a new line, or overwrites the last line with the
        information about the current scan. Last line should
        be overwritten when adding a new series

        Args:
            overwrite_line (bool): Whether or not to overwrite the last line

        """
        name_for_csv = self.scan_name
        if self.scan_part_count > 1:
            name_for_csv += '-{}ofX'.format(self.scan_part_count)

        scan_details = os.path.join(self.base_dir, 'scan_details.csv')
        if not overwrite_line:
            # create new line
            with open(scan_details, 'a') as csv_file:
                csv_file.write('{},{}\n'.format(
                    name_for_csv,
                    str(self.scans[self.scan_part_id][self.scan_part_count - 1])
                ))
        else:
            # overwrite the last line, just need to increment series count
            lines = []
            with open(scan_details, 'r') as csv_file:
                lines = csv_file.readlines()

            lines[-1] = '{},{}\n'.format(
                name_for_csv,
                str(self.scans[self.scan_part_id][self.scan_part_count - 1])
            )
            with open(scan_details, 'w') as csv_file:
                for line in lines:
                    csv_file.write(line)

    def update_scan_progress(self, current_scan):
        """Updates progress of the scan

        Args:
            current_scan (str): Name of the current scan

        """
        total_scans = self.turntable.photos_per_scan + 2
        self.total_scan_label.setText(str(total_scans))
        self.current_scan_label.setText(str(current_scan))
        self.scan_progress.setValue(100 * current_scan / total_scans)

    def perform_scan_cycle(self):
        """Initiates a scan cycle

        """
        cam_list = range(len(self.cameras))
        print('~===-*^% Photos per scan {}'.format(self.turntable.photos_per_scan))

        # Drain the event queue from anything that may have happened outside of the
        # wayscan application
        coroutines = []
        for cam_num in cam_list:
            coroutines.append(self.cameras[cam_num].clear_events(3.0))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*coroutines))

        self.update_scan_progress(0)
        for shot in range(self.turntable.photos_per_scan):
            print('=============== LOOPING ================')
            if shot > 0:
                self.turntable.rotate_slice()
                self.textEdit.append('Delay {:.2f}sec'.format(self.turntable.delay))
                time.sleep(self.turntable.delay)
            self.take_photo_for_cams(cam_list, True, 'scan')

            self.update_scan_progress(shot + 1)

            # Ensure that the GUI updates to show the new preview
            Qtw.QApplication.processEvents()

        self.show_message_box(
            'Take Photo',
            'Background Shot',
            'Take a photo of the empty stage for a background shot',
            'Remove object and then click the `Take Photo` button to shoot the empty stage and background',
            get_pixmap('background.png')
        )
        self.take_photo_for_cams(cam_list, True, 'background')
        self.update_scan_progress(self.turntable.photos_per_scan + 1)

        Qtw.QApplication.processEvents()
        self.show_message_box(
            'Take Photo',
            'Color Checker',
            'Take photo of the stage with the color checker',
            'Ensure color checker is visible in each camera of the cameras and the click `Take Photo` button',
            get_pixmap('colorcard.png')
        )
        self.take_photo_for_cams(cam_list, True, 'colorcard')
        self.update_scan_progress(self.turntable.photos_per_scan + 2)

        Qtw.QApplication.processEvents()
        print(self.scans)

    def show_message_box(self, button_text, title, text, informative_text=None, image=None, is_choice=False, no_button_text=None):
        """Helper for displaying a messagebox

        Args:
            button_text (str): Text to display on the button
            title (str): Title for the message box
            text (str): Text to display on the message box
            informative_text (str): Additional text to display on message box
            image (str): Path to image to display on message box
            is_choice (bool): Whether this is a yes/no message box or just information
            no_button_text (str): Text to display on the no/cancel button

        Returns:
            bool: Return value from the messagebox

        """
        msgbox = msgdialog.MessageDialog(
            button_text,
            title,
            text,
            informative_text,
            image,
            is_choice,
            no_button_text
        )
        return msgbox.exec_()

    def take_photo_for_cams(self, which_cams, for_scan=False, type=None):
        """Takes photos for each of the cameras

        Args:
            which_cams ([int]): List of camera numbers fo take pictures for_scan
            for_scan (bool): Whether this photo is for scan or test
            type (str): Type of image (scan, background, colorcard)

        """
        # Name the bucket that we want to associate these images with
        association = 'initialization'
        self.textEdit.append('Triggering Cameras')
        Qtw.QApplication.processEvents()

        series = None
        if for_scan:
            series = self.scans[self.scan_part_id][self.scan_part_count - 1].num_series
            full_scan_name = self.scan_part_id
            if self.scan_part_count > 1:
                full_scan_name += '-{}ofX'.format(self.scan_part_count)
            association = full_scan_name

        coroutines = []
        for cam_num in which_cams:
            coroutines.append(self.cameras[cam_num].take_photo(association))

        loop = asyncio.get_event_loop()
        responses = loop.run_until_complete(asyncio.gather(*coroutines))

        with open(os.path.join(self.base_dir, 'image_map.csv'), 'a') as csv_file:
            for i, cam_num in enumerate(which_cams):
                response = responses[i]

                # if response is not none then the camera shot succeeded
                if response is not None and len(response) > 0:
                    cam = self.cameras[cam_num]
                    self.cam_counters[cam_num].display(cam.number_of_photos_taken)

                    # Grab the thumbnail of the image to display, this way we can get an
                    # idea for the quality.
                    # @TODO see if we can get something higher quality than the thumbnail
                    #       can call Camera.get_lens_preview() for higher detail - a little slower
                    preview = cam.get_preview(response['file'], response['dir'])
                    if preview is not None:
                        preview_pixmap = Qtg.QPixmap()
                        preview_pixmap.loadFromData(preview)

                        thumbnail = self.cam_previews[cam_num]
                        thumbnail.setPixmap(preview_pixmap.scaled(thumbnail.width(), thumbnail.height(), Qtc.Qt.KeepAspectRatio))

                    self.textEdit.append('Cam {}: {}'.format(cam_num + 1, response['file']))

                    image = ImageAssociation(
                        response['file'],
                        response['dir'],
                        cam_num,
                        association,
                        series,
                        type,
                        cam.aperture,
                        cam.ISO,
                        cam.shutter_speed
                    )
                    self.image_associations.append(image)
                    csv_file.write(str(image))

    def initialization_shot(self):
        """Takes initialization shot for all attached cameras

        """
        self.create_files_if_necessary()
        # Set tab to camera preview tabWidget
        self.tabWidget.setCurrentIndex(THUMBNAIL_TAB_INDEX)
        print('============ Taking initialization shots ===============')
        which_cams = range(len(self.cameras))
        self.take_photo_for_cams(which_cams)

        # Update camera settings for initialization shots
        for i, cam_num in enumerate(which_cams):
            self.cameras[cam_num].load_config_settings()

        self.refresh_camera_settings()

    def update_config(self):
        """This method is called any time our configuration has changed

        We need to update the application's conf file and also apply the configuration
        changes to ensure proper operation.

        """
        print('Updating Config File')
        with open(consts.CONFIG_FILE, 'w+') as config_file:
            self.config.write(config_file)

    def create_files_if_necessary(self):
        """Creates the required directory and CSV files

        """
        # Make the base_dir now, so we can write image data to it realtime
        os.makedirs(self.base_dir, exist_ok=True)

        image_map = os.path.join(self.base_dir, 'image_map.csv')
        if not os.path.exists(image_map):
            # generate the image association file
            with open(image_map, 'w+') as csv_file:
                # Header
                csv_file.write('File,Scan ID,Series Num,Camera Num,Image Type,Aperture,ISO,Shutter,Directory\n')

        scan_details = os.path.join(self.base_dir, 'scan_details.csv')
        if not os.path.exists(scan_details):
            # generate the scan details text file
            with open(scan_details, 'w+') as csv_file:
                # Camera Header
                csv_file.write('Camera Details\nCam Position,Cam Model,Serial,Lens\n')
                for cam in self.cameras:
                    csv_file.write('{},{},{},{}\n'.format(cam.position, cam.model, cam.serial_num, cam.lens))

                # Scan Header
                csv_file.write('\nScan Details\nScan ID,Number of Series,Scan Type,Object Type,Scan Notes,Scan Name,Generate 3D Model?\n')

class ImageAssociation():
    def __init__(self, file_path, dir, camera, scan_name, series, image_type, aperture, ISO, shutter_speed):
        self.camera_number = camera
        self.scan_name = scan_name
        self.series = series
        self.image_type = image_type
        self.aperture = aperture
        self.ISO = ISO
        self.shutter_speed = shutter_speed
        self.file_path = file_path
        self.dir = dir

    def __repr__(self):
        """How the object should be represented when casted to string

        """
        xstr = lambda v: '' if v is None else v
        return '{},{},{},{},{},{},{},{},{}\n'.format(
            self.file_path,
            xstr(self.scan_name),
            xstr(self.series),
            self.camera_number,
            xstr(self.image_type),
            xstr(self.aperture),
            xstr(self.ISO),
            xstr(self.shutter_speed),
            self.dir
        )


class ScanDetails():
    def __init__(self, num_series, scan_type, object_type, notes, scan_name, generate_3d_model):
        self.num_series = num_series
        self.scan_type = scan_type
        self.object_type = object_type
        self.notes = notes
        self.scan_name = scan_name
        self.generate_3d_model = generate_3d_model

    def __repr__(self):
        """How the object should be represented when casted to string

        """
        return '{},{},{},"{}","{}",{}'.format(
            self.num_series,
            self.scan_type,
            self.object_type,
            self.notes.replace('"', '""'),
            self.scan_name.replace('"', '""'),
            self.generate_3d_model
        )


def get_pixmap(name):
    path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(path, name)
    return Qtg.QPixmap(image_path)


# I feel better having one of these
def main():
    usbcontroller.turn_ethernet_off()
    atexit.register(usbcontroller.enable_all_usb)

    # a new app instance
    consts.app = Qtw.QApplication(sys.argv)
    consts.app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    splash_image = get_pixmap('splash.jpg')
    splash = Qtw.QSplashScreen(splash_image)
    splash.show()
    consts.app.processEvents()

    # the main GUI window
    form = MainWindow(splash)
    form.show()
    splash.finish(form)

    # without this, the script exits immediately.
    sys.exit(consts.app.exec_())

# python bit to figure how who started This
if __name__ == "__main__":
    main()
