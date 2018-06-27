import sys
import PyQt5
from PyQt5.QtWidgets import *
import initdialog_auto
import gphoto2 as gp
import configparser as conf
import collections
from camerafactory import CameraFactory


class InitDialog(QDialog, initdialog_auto.Ui_Dialog):
    def __init__(self, config):
        super().__init__()
        self.setupUi(self)

        self.serials = []
        self.config = config

        self.camera_combos = []
        self.camera_combos.append(self.camera_combo_1)
        self.camera_combos.append(self.camera_combo_2)
        self.camera_combos.append(self.camera_combo_3)
        self.camera_combos.append(self.camera_combo_4)
        
        # try to get camera settings from config file
        if self.config and 'CAMERAS' in self.config:
            camera_settings = self.config['CAMERAS']
            for cam_num, camera_combo in enumerate(self.camera_combos):
                camera_combo.addItem(camera_settings.get('Camera{}Serial'.format(cam_num + 1), '- No Camera Set -'))
                camera_combo.setEnabled(False)
        else:
            if self.config is None:
                self.config = conf.ConfigParser()
                self.config.read('/home/pi/.quickcapture.conf')

            self.reset_camera_serial_options()

        self.camera_reset_button.clicked.connect(self.reset_camera_serial_options)

    def reset_camera_serial_options(self):
        serial_options = []
        for camera_combo in self.camera_combos:
            while camera_combo.count() > 0:
                camera_combo.removeItem(0)
                                     
            serial_options.append('- Select Camera Serial -')
            serial_options.extend(CameraFactory.get_instance().get_camera_serials())
            camera_combo.setEnabled(True)
            camera_combo.addItems(serial_options)

    def accept(self):
        cams = {}
        for cam_num, camera_combo in enumerate(self.camera_combos):
            if camera_combo.currentIndex():
                cams['Camera{}Serial'.format(cam_num + 1)] = camera_combo.currentText()

        if len(cams) > 0:
            self.config['CAMERAS'] = collections.OrderedDict(sorted(cams.items()))

        super().accept()
