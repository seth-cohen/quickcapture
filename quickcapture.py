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
import turntable
import time

# This is our window from QtCreator
import mainwindow_auto as main
import configdialog

app = None
EFAULT_DELAY = 5.0
DEFAULT_TURNTABLE_PERIOD = 31
DEFAULT_PHOTOS_PER_SCAN = 18
DEFAULT_CAM_1_PIN = 6
DEFAULT_CAM_2_PIN = 10
DEFAULT_CAM_3_PIN = 11
DEFAULT_CAM_4_PIN = 31

# create class for our Raspberry Pi GUI
class MainWindow(Qtw.QMainWindow, main.Ui_MainWindow):
    # access variables inside of the UI's file
    def __init__(self):
        super().__init__()
        self.setupUi(self) # gets defined in the UI file

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
            int(turntable_data.get('timetorotate', 31)),
            int(turntable_data.get('photosperscan', 18)),
            float(turntable_data.get('delay', 5.0))
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
        path = os.path.dirname(os.path.abspath(__file__))
        preview_image_path = os.path.join(path, 'cam_preview.png')
        print(preview_image_path)
        for preview in self.cam_previews:
            preview.setPixmap(Qtg.QPixmap(preview_image_path).scaled(preview.width(), preview.height(), Qtc.Qt.KeepAspectRatio))

        self.initialize_button.clicked.connect(self.initialization_shot)
        self.new_scan_button.clicked.connect(self.start_scan)
        self.pushButton.clicked.connect(self.display_config)
        self.ftp_button.clicked.connect(self.display_ftp)
        self.actionClose.triggered.connect(self.close)
        self.actionConfig.triggered.connect(self.display_config)

    def generate_default_config(self):
       self.config['DEFAULTS'] = {
           'camera1pin': 6,
           'camera2pin': 10,
           'camera3pin': 11,
           'camera4pin': 31
       }
       self.config['TURNTABLE'] = {
           'timetorotate': 31,
           'photosperscan': 18,
           'delay': 5.0
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
        for shot in range(self.turntable.photos_per_scan):
            for cam_num, cam in enumerate(self.cameras):
                cam.take_photo()
                self.cam_counters[cam_num].display(cam.number_of_photos_taken)
                

            app.processEvents()
            self.turntable.rotate_slice()

    def initialization_shot(self):
        print('Initializing...')
        for cam_num, cam in enumerate(self.cameras):
            print('Initializing camera.Camera {}'.format(cam_num + 1))
            cam.take_photo()
            self.cam_counters[cam_num].display(cam.number_of_photos_taken)
            preview = cam.get_preview()
            if preview is not None:
                preview_pixmap = Qtg.QPixmap()
                preview_pixmap.loadFromData(preview)

                thumbnail = self.cam_previews[cam_num]
                thumbnail.setPixmap(preview_pixmap.scaled(thumbnail.width(), thumbnail.height(), Qtc.Qt.KeepAspectRatio))

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
