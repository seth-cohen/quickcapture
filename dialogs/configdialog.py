import sys
import PyQt5
import PyQt5.QtWidgets as Qtw
import gphoto2 as gp
import configparser as conf
import collections
import Crypto.Cipher.AES as AES
import Crypto.Random as rand
import base64

import camerafactory as cf
import dialogs.configdialog_auto as configdialog_auto
import consts


class ConfigDialog(Qtw.QDialog, configdialog_auto.Ui_ConfigDialog):
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
        else:
            self.reset_camera_serial_options()

        turntable_settings = config['TURNTABLE']
        self.turntable_period.setText(turntable_settings.get('timetorotate', consts.DEFAULT_TURNTABLE_PERIOD))
        self.photos_per_scan.setText(turntable_settings.get('photosperscan', consts.DEFAULT_PHOTOS_PER_SCAN))

        ftp_settings = config['FTP']
        self.host.setText(ftp_settings.get('host', consts.DEFAULT_FTP_HOST))
        self.username.setText(ftp_settings.get('username', ''))

        # decrypt the hashed password
        hash = base64.b64decode(ftp_settings.get('h', ''))
        tag = base64.b64decode(ftp_settings.get('t', ''))
        nonce = base64.b64decode(ftp_settings.get('n', ''))
        key = base64.b64decode(ftp_settings.get('k', ''))
        pw = ''
        if len(hash) > 0 and len(tag) > 0 and len(nonce) > 0 and len(key) > 0:
            cipher = AES.new(key, AES.MODE_EAX, nonce)
            pw = cipher.decrypt_and_verify(hash, tag).decode('utf-8')
            self.password.setText(pw)
            
        if  len(pw) > 0 and len(ftp_settings.get('username', '')) > 0:
            self.password.setReadOnly(True)
            self.username.setReadOnly(True)
        
        # Attach handlers for buttons
        self.camera_reset_button.clicked.connect(self.reset_camera_serial_options)
        self.camera_search_button.clicked.connect(self.refresh_camera_list)
        self.unlock_ftp_button.clicked.connect(self.unlock_ftp_settings)

    def refresh_camera_list(self):
        cf.CameraFactory.get_instance().reset_cameras()
        
    def reset_camera_serial_options(self):
        serial_options = ['- Select Camera Serial -']
        serial_options.extend(cf.CameraFactory.get_instance().get_camera_serials())
        for camera_combo in self.camera_combos:
            while camera_combo.count() > 0:
                camera_combo.removeItem(0)
                                     
            camera_combo.addItems(serial_options)

    def unlock_ftp_settings(self):
        self.password.setReadOnly(False)
        self.username.setReadOnly(False)
   
    def accept(self):
        cams = {}
        for cam_num, camera_combo in enumerate(self.camera_combos):
            if camera_combo.currentIndex():
                cams['Camera{}Serial'.format(cam_num + 1)] = camera_combo.currentText()

        if len(cams) > 0:
            self.config['CAMERAS'] = collections.OrderedDict(sorted(cams.items()))
        elif len(self.config['CAMERAS']) == 0:
            return Qtw.QMessageBox.critical(self, 'Camera Error', 'Please select camera locations')

        self.config['TURNTABLE']['timetorotate'] = self.turntable_period.text()
        self.config['TURNTABLE']['photosperscan'] = self.photos_per_scan.text()
        
        self.config['FTP']['username'] = self.username.text()
        if len(self.password.text()) > 0:
            # just going to store all these in the conf file, not really concerned with too
            # much security just something that obfuscates a bit
            key = rand.get_random_bytes(16)
            cipher = AES.new(key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(self.password.text().encode('utf-8'))

            self.config['FTP']['h'] = base64.b64encode(ciphertext).decode('utf-8')
            self.config['FTP']['t'] = base64.b64encode(tag).decode('utf-8')
            self.config['FTP']['n'] = base64.b64encode(cipher.nonce).decode('utf-8')
            self.config['FTP']['k'] = base64.b64encode(key).decode('utf-8')

        super().accept()
