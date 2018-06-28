import sys
import PyQt5
import PyQt5.QtWidgets as Qtw
import configdialog_auto
import gphoto2 as gp
import configparser as conf
import collections
import camerafactory as cf


class ConfigDialog(Qtw.QDialog, configdialog_auto.Ui_Dialog):
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

        if self.config is None:
            self.config = conf.ConfigParser()
            self.config.read('/home/pi/.quickcapture.conf')
            
        # try to get camera settings from config file
        if 'CAMERAS' in self.config:
            camera_settings = self.config['CAMERAS']
            for cam_num, camera_combo in enumerate(self.camera_combos):
                camera_combo.addItem(camera_settings.get('Camera{}Serial'.format(cam_num + 1), '- No Camera Set -'))
                camera_combo.setEnabled(False)
        else:
            self.reset_camera_serial_options()

        turntable_settings = config['TURNTABLE']
        self.turntable_period.setText(turntable_settings.get('timetorotate', str(31)))
        self.photos_per_scan.setText(turntable_settings.get('photosperscan', str(18)))

        ftp_settings = config['FTP']
        self.host.setText(ftp_settings.get('host', 'FTPPartner.wayfair.com'))
        self.username.setText(ftp_settings.get('username', ''))
        self.password.setText(ftp_settings.get('hash', ''))
        if len(ftp_settings.get('hash', '')) > 0 and len(ftp_settings.get('username', '')) > 0:
            self.password.setEnabled(False)
            self.username.setEnabled(False)
        
        # Attach handlers for buttons
        self.camera_reset_button.clicked.connect(self.reset_camera_serial_options)
        self.unlock_ftp_button.clicked.connect(self.unlock_ftp_settings)

    def reset_camera_serial_options(self):
        serial_options = ['- Select Camera Serial -']
        serial_options.extend(cf.CameraFactory.get_instance().get_camera_serials())
        for camera_combo in self.camera_combos:
            while camera_combo.count() > 0:
                camera_combo.removeItem(0)
                                     
            camera_combo.setEnabled(True)
            camera_combo.addItems(serial_options)

    def unlock_ftp_settings(self):
        self.password.setEnabled(True)
        self.username.setEnabled(True)
   
    def accept(self):
        cams = {}
        for cam_num, camera_combo in enumerate(self.camera_combos):
            if camera_combo.currentIndex():
                cams['Camera{}Serial'.format(cam_num + 1)] = camera_combo.currentText()

        if len(cams) > 0:
            self.config['CAMERAS'] = collections.OrderedDict(sorted(cams.items()))

        self.config['TURNTABLE']['timetorotate'] = self.turntable_period.text()
        self.config['TURNTABLE']['photosperscan'] = self.photos_per_scan.text()
        
        self.config['FTP']['username'] = self.username.text()
        if len(self.password.text()) > 0:
            self.config['FTP']['hash'] = self.password.text()

        super().accept()
