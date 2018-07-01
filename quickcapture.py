# This gets the Qt stuff
import sys
import PyQt5
import PyQt5.QtWidgets as Qtw
import PyQt5.QtGui as Qtg
import PyQt5.QtCore as Qtc
import wiringpi as wpi
import os

# styling
import qdarkstyle

import configparser
import camera
import consts
import turntable
import time

# This is our window from QtCreator
import mainwindow_auto as main
import dialogs.configdialog as configdialog
import dialogs.ftpdialog as ftpdialog
import dialogs.newscandialog as scandialog
import dialogs.messagedialog as msgdialog


# create class for our Raspberry Pi GUI
class MainWindow(Qtw.QMainWindow, main.Ui_MainWindow):
    # access variables inside of the UI's file
    def __init__(self):
        super().__init__()
        self.setupUi(self) # gets defined in the UI file
        self.connect_ui()

        self.scans = {}
        self.last_scan_name = ''
        self.scan_part_count = 1

        self.config = configparser.ConfigParser()
        self.config.read(consts.CONFIG_FILE)
        # if we don't already have a config file we should generate one
        if len(self.config.sections()) == 0:
            print('No Config file present')
            self.generate_default_config()
            self.display_config()

        self.setup_hardware()
        self.reset_previews()
        
    def setup_hardware(self):
        self.cameras = [];
        for x in range(0, 4):
            self.cameras.append(camera.Camera(self.config['DEFAULTS']['camera{}pin'.format(x + 1)], self.config['CAMERAS'].get('camera{}serial'.format(x + 1), None), x))

        turntable_data = self.config['TURNTABLE']
        self.turntable = turntable.Turntable(
            int(turntable_data.get('turntablepin', consts.DEFAULT_TURNTABLE_PIN)),
            int(turntable_data.get('timetorotate', consts.DEFAULT_TURNTABLE_PERIOD)),
            int(turntable_data.get('photosperscan', consts.DEFAULT_PHOTOS_PER_SCAN)),
            float(turntable_data.get('delay', consts.DEFAULT_DELAY))
        )
        
    def connect_ui(self):
        self.cam_counters = []
        self.cam_counters.append(self.image_count_1)
        self.cam_counters.append(self.image_count_2)
        self.cam_counters.append(self.image_count_3)
        self.cam_counters.append(self.image_count_4)

        self.cam_previews = []
        self.cam_previews.append(self.thumbnail_1)
        self.cam_previews.append(self.thumbnail_2)
        self.cam_previews.append(self.thumbnail_3)
        self.cam_previews.append(self.thumbnail_4)
        
        self.initialize_button.clicked.connect(self.initialization_shot)
        self.new_scan_button.clicked.connect(self.start_scan)
        self.ftp_button.clicked.connect(self.display_ftp)
        self.actionClose.triggered.connect(self.close)
        self.actionConfig.triggered.connect(self.display_config)

    def reset_previews(self):
        """Place camera preview placeholder in place of the live feeds
        
        """
        path = os.path.dirname(os.path.abspath(__file__))
        preview_image_path = os.path.join(path, 'cam_no_preview.png')
        print(preview_image_path)
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

    def display_ftp(self):
        ftp = ftpdialog.FTPDialog(self.config, self.cameras)
        if ftp.exec():
            # reset camera counts etc.            
            pass
        
    def close(self):
        exit()
        
    def start_scan(self):
        dialog = scandialog.NewScanDialog(len(self.scans) == 0, self.last_scan_name)
        if dialog.exec_():
            scan_name = dialog.scan_name
            if dialog.is_additional_part:
                self.scan_part_count += 1
            else:
                self.scan_part_count = 1

            if self.scan_part_count > 1:
                self.scan_name_label.setText('{} (Part {})'.format(scan_name, self.scan_part_count))
                self.scans[scan_name].append(1)
            else:
                self.scan_name_label.setText(scan_name)
                self.scans[scan_name] = [1]
                
            self.perform_scan_cycle()

            orientation_image = Qtg.QPixmap()
            orientation_image.load('orientation.png')
            while self.show_message_box(
                'Start Scan Cycle',
                'New Orientation',
                'Would you like to shoot an additional orientation of this part?',
                ('If you would like to shoot a new orientation of this same part'
                ' place it on it\'s side and click `Start Scan Cycle` button'),
                orientation_image,
                True
            ):
                self.perform_scan_cycle()
                self.scans[scan_name][self.scan_part_count - 1] += 1

            self.last_scan_name = scan_name
            print(self.scans)
                
    def perform_scan_cycle(self):
        cam_list = range(len(self.cameras))
        for shot in range(self.turntable.photos_per_scan):
            self.take_photo_for_cams(cam_list)

            consts.app.processEvents()
            self.turntable.rotate_slice()

        background_image = Qtg.QPixmap()
        background_image.load('background.png')
        self.show_message_box(
            'Take Photo',
            'Background Shot',
            'Take a photo of the empty stage for a background shot',
            'Remove object and then click the `Take Photo` button to shoot the empty stage and background',
            background_image
        )
        self.take_photo_for_cams(cam_list)

        checker_image = Qtg.QPixmap()
        checker_image.load('colorcard.png')
        self.show_message_box(
            'Take Photo',
            'Color Checker',
            'Take photo of the stage with the color checker',
            'Ensure color checker is visible in each camera of the cameras and the click `Take Photo` button',
            checker_image
        )
        self.take_photo_for_cams(cam_list)

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
        
    def take_photo_for_cams(self, which_cams):
        for cam_num in which_cams:
            cam = self.cameras[cam_num]
            cam.take_photo()
            self.textEdit.append(cam.get_new_photo()) 
            self.cam_counters[cam_num].display(cam.number_of_photos_taken)
            preview = cam.get_preview()
            if preview is not None:
                preview_pixmap = Qtg.QPixmap()
                preview_pixmap.loadFromData(preview)

                thumbnail = self.cam_previews[cam_num]
                thumbnail.setPixmap(preview_pixmap.scaled(thumbnail.width(), thumbnail.height(), Qtc.Qt.KeepAspectRatio))
                
    def initialization_shot(self):
        print('Taking initialization shots')
        self.take_photo_for_cams(range(len(self.cameras)))

    def update_config(self):
        """This method is called any time our configuration has changed

        We need to update the application's conf file and also apply the configuration 
        changes to ensure proper operation.

        """
        print('Updating Config File')
        with open(consts.CONFIG_FILE, 'w+') as config_file:
            self.config.write(config_file)

    def toggle_pin(self, pin):
        if wpi.digitalRead(pin) == 1:
            wpi.digitalWrite(pin, 0)
        else:
            wpi.digitalWrite(pin, 1)
        
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
