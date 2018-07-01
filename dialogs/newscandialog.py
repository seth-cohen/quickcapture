import sys
import PyQt5
import PyQt5.QtWidgets as Qtw
import dialogs.newscandialog_auto as newscandialog_auto

NEW_PRODUCT = 0
ADDITIONAL_PART = 1


class NewScanDialog(Qtw.QDialog, newscandialog_auto.Ui_NewScanDialog):
    def __init__(self, is_first=False, scan_name=''):
        super().__init__()
        self.setupUi(self)
        
        self.scan_name = scan_name
        self.is_additional_part = False
        
        if scan_name == '':
            self.scan_name_input.setEnabled(True)

        self.scan_type.currentIndexChanged.connect(self.scan_type_changed)
        self.start_scan_button.clicked.connect(self.start_scan)
        self.cancel_button.clicked.connect(self.reject)

    def start_scan(self):
        self.scan_name = self.scan_name_input.text()
        if self.scan_name == '':
            Qtw.QMessageBox.about(self, 'Error', 'Please enter name for scan')
            return

        if self.scan_type.currentIndex == ADDITIONAL_PART:
            self.scan_name += '(Part {})'.format(self.parts_count)

        msgbox = Qtw.QMessageBox(self)
        msgbox.addButton('Ready', Qtw.QMessageBox.AcceptRole)
        msgbox.setWindowTitle('Prepare For Scan')
        msgbox.setText('Place the object to scan on the turntable')
        msgbox.exec()
        self.accept()

        
    def scan_type_changed(self, i):
        if i == ADDITIONAL_PART:
            self.scan_name_input.setText(self.scan_name)
            self.scan_name_input.setEnabled(False)
            self.is_additional_part = True
        else:
            self.scan_name_input.setText('')
            self.scan_name_input.setEnabled(True)
            self.is_additional_part = False
