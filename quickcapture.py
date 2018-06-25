# This gets the Qt stuff
import sys
import PyQt5
from PyQt5.QtWidgets import *
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
import wiringpi as wpi

import os
import configparser
from camera import Camera
from turntable import Turntable
import time

# This is our window from QtCreator
import mainwindow_auto

app = None

# create class for our Raspberry Pi GUI
class MainWindow(QMainWindow, mainwindow_auto.Ui_MainWindow):
    # access variables inside of the UI's file
    def __init__(self):
        super().__init__()
        self.setupUi(self) # gets defined in the UI file

        config = configparser.ConfigParser()
        config.read('/home/pi/.quickcapture.conf')
        print(config.sections())
        
        turntable_data = config['TURNTABLE']
        self.turntable = Turntable(int(turntable_data['TimeToRotate']), int(turntable_data['PhotosPerScan']))

        self.cameras = [];
        for x in range(0, 4):
            self.cameras.append(Camera(config['DEFAULTS']['Camera{}Pin'.format(x + 1)]))

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
            preview.setPixmap(Gui.QPixmap(preview_image_path).scaled(preview.width(), preview.height(), Core.Qt.KeepAspectRatio))

        self.initialize_button.clicked.connect(self.initialization_shot)
        self.start_button.clicked.connect(self.start_scan)
        
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
            print('Initializing Camera {}'.format(cam_num + 1))
            cam.take_photo()
            self.cam_counters[cam_num].display(cam.number_of_photos_taken)

    def toggle_pin(self, pin):
        if wpi.digitalRead(pin) == 1:
            wpi.digitalWrite(pin, 0)
        else:
            wpi.digitalWrite(pin, 1)
        
# I feel better having one of these
def main():
    # a new app instance
    global app
    QApplication.setStyle('Fusion')
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    
    # without this, the script exits immediately.
    sys.exit(app.exec_())
 
# python bit to figure how who started This
if __name__ == "__main__":
    main()
