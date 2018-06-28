import os
import PyQt5.QtWidgets as Qtw
import PyQt5.QtCore as Qtc
import PyQt5.QtGui as Qtg
import dialogs.ftpdialog_auto as ftpdialog_auto
import configparser as conf
import consts


class FTPDialog(Qtw.QDialog, ftpdialog_auto.Ui_FTPDialog):
    def __init__(self, config):
        super().__init__()
        self.setupUi(self)

        self.config = config
        path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(path, 'logo.png')
        self.logo.setPixmap(Qtg.QPixmap(logo_path).scaled(self.logo.width(), self.logo.height(), Qtc.Qt.KeepAspectRatio))

        if self.config is None:
            self.config = conf.ConfigParser()
            self.config.read('/home/pi/.quickcapture.conf')
    
        ftp_settings = self.config['FTP']
        self.host.setText(ftp_settings.get('host',  consts.DEFAULT_FTP_HOST))
        self.username.setText(ftp_settings.get('username', ''))

