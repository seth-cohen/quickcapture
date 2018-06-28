# This gets the Qt stuff
import sys
import PyQt5
import PyQt5.QtWidgets as Qtw
import PyQt5.QtGui as Qtg
import PyQt5.QtCore as Qtc
import wiringpi as wpi

import os
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

app = None

# create class for our Raspberry Pi GUI
class MainWindow(Qtw.QMainWindow, main.Ui_MainWindow):
    # access variables inside of the UI's file
    def __init__(self):
        super().__init__()
        self.setupUi(self) # gets defined in the UI file

        self.scans = {}
        self.last_scan_name = ''

        self.config = configparser.ConfigParser()
        self.config.read('/home/pi/.quickcapture.conf')
        # if we don't already have a config file we should generate one
        if len(self.config.sections()) == 0:
            print('No Config file present')
            self.generate_default_config()
            self.display_config()

        self.ui()

        self.cameras = [];
        for x in range(0, 4):
            self.cameras.append(camera.Camera(self.config['DEFAULTS']['camera{}pin'.format(x + 1)], self.config['CAMERAS'].get('camera{}serial'.format(x + 1), None)))

    def ui(self):
        turntable_data = self.config['TURNTABLE']
        self.turntable = turntable.Turntable(
            int(turntable_data.get('turntablegpio', consts.DEFAULT_TURNTABLE_PIN)),
            int(turntable_data.get('timetorotate', consts.DEFAULT_TURNTABLE_PERIOD)),
            int(turntable_data.get('photosperscan', consts.DEFAULT_PHOTOS_PER_SCAN)),
            float(turntable_data.get('delay', consts.DEFAULT_DELAY))
        )

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

        # Place camera preview placeholder in place of the live feeds
        path = os.path.dirname(os.path.abspath(__file__))
        preview_image_path = os.path.join(path, 'cam_preview.png')
        print(preview_image_path)
        for preview in self.cam_previews:
            preview.setPixmap(Qtg.QPixmap(preview_image_path).scaled(preview.width(), preview.height(), Qtc.Qt.KeepAspectRatio))

        self.initialize_button.clicked.connect(self.initialization_shot)
        self.new_scan_button.clicked.connect(self.start_scan)
        self.ftp_button.clicked.connect(self.display_ftp)
        self.actionClose.triggered.connect(self.close)
        self.actionConfig.triggered.connect(self.display_config)

    def generate_default_config(self):
        """Sets the known defaults for the config file.
        If there is no pre-generated config file at ~/.quickcapture.conf this method
        should be called prior to completing initialization so that we can generate 
        the config file with appropriate default values"""
        self.config['DEFAULTS'] = {
            'camera1pin': consts.DEFAULT_CAM_1_PIN,
            'camera2pin': consts.DEFAULT_CAM_2_PIN,
            'camera3pin': consts.DEFAULT_CAM_3_PIN,
            'camera4pin': consts.DEFAULT_CAM_4_PIN
        }
        self.config['TURNTABLE'] = {
            'timetorotate': consts.DEFAULT_TURNTABLE_PERIOD,
            'photosperscan': consts.DEFAULT_PHOTOS_PER_SCAN,
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

    def display_ftp(self):
        ftp = ftpdialog.FTPDialog(self.config)
        if ftp.exec():
            # reset camera counts etc.            
            pass
        
    def close(self):
        exit()
        
    def start_scan(self):
        dialog = scandialog.NewScanDialog(len(self.scans) == 0, self.last_scan_name)
        if dialog.exec_():
            scan_name = dialog.scan_name
            self.perform_scan_cycle()
            self.scans[scan_name] = 1
            self.scan_name_label.setText(scan_name)

            while Qtw.QMessageBox.question(
                    self,
                    'New Orientation',
                    'Would you like to scan an additional orientation of this part?'
                    ) == Qtw.QMessageBox.Yes:
                self.perform_scan_cycle()
                self.scans[scan_name] += 1

            self.last_scan_name = scan_name
                
    def perform_scan_cycle(self):
        cam_list = range(len(self.cameras))
        for shot in range(self.turntable.photos_per_scan):
            self.take_photo_for_cams(cam_list)

            app.processEvents()
            self.turntable.rotate_slice()

        self.show_message_box(
            'Take Photo',
            'Background Shot',
            'Take a photo of the empty stage for a background shot',
            'Remove object and then take photo'
        )
        self.take_photo_for_cams(cam_list)

        self.show_message_box(
            'Take Photo',
            'Color Checker',
            'Take photo of the stage with the color checker',
            'Ensure color checker is visible in each camera'
        )
        self.take_photo_for_cams(cam_list)

    def show_message_box(self, button_text, title, text, informative_text=None):
        msgbox = Qtw.QMessageBox(self)
        msgbox.addButton(button_text, Qtw.QMessageBox.AcceptRole)
        msgbox.setWindowTitle(title)
        msgbox.setText(text)
        if informative_text is not None:
            msgbox.setInformativeText(informative_text)
        return msgbox.exec()
        
    def take_photo_for_cams(self, which_cams):
        for cam_num in which_cams:
            cam = self.cameras[cam_num]
            cam.take_photo()
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
        print('Updating Config File')
        with open('/home/pi/.quickcapture.conf', 'w+') as config_file:
            self.config.write(config_file)

    def toggle_pin(self, pin):
        if wpi.digitalRead(pin) == 1:
            wpi.digitalWrite(pin, 0)
        else:
            wpi.digitalWrite(pin, 1)
        
# I feel better having one of these
def main():
    # a new app instance
    global app
    Qtw.QApplication.setStyle('Fusion')
    app = Qtw.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    
    # without this, the script exits immediately.
    sys.exit(app.exec_())
 
# python bit to figure how who started This
if __name__ == "__main__":
    main()
