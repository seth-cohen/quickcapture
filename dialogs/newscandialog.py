import sys
import PyQt5
import PyQt5.QtWidgets as Qtw
import dialogs.newscandialog_auto as newscandialog_auto

NEW_PRODUCT = 0
ADDITIONAL_PART = 1

SKU = 0
PROP = 1
EXPERIMENT = 2
OTHER = 3

class NewScanDialog(Qtw.QDialog, newscandialog_auto.Ui_NewScanDialog):
    def __init__(self, is_first=False, scan_name=''):
        super().__init__()
        self.setupUi(self)
        
        self.scan_name = scan_name
        self.is_additional_part = False
        self.scan_notes = ''
        
        if scan_name == '':
            self.scan_name_input.setReadOnly(False)
            self.subject_type.model().item(1).setSelectable(False)

        self.scan_type = 'SKU'
        self.subject_type.currentIndexChanged.connect(self.subject_type_changed)
        self.start_scan_button.clicked.connect(self.start_scan)
        self.cancel_button.clicked.connect(self.reject)

    def start_scan(self):
        self.scan_name = self.scan_name_input.text()
        if self.scan_name == '':
            Qtw.QMessageBox.about(self, 'Error', 'Please enter name for scan')
            return

        if self.subject_type.currentIndex == ADDITIONAL_PART:
            self.scan_name += '(Part {})'.format(self.parts_count)

        self.scan_notes = self.scan_notes_input.toPlainText()
        self.scan_type = self.scan_type_input.currentText()

        Qtw.QMessageBox.warning(
            self,
            'Prepare For Scan',
            'Before clicking `OK`, ensure that camera settings are correct and in focus. Then place the object to scan on the turntable.'
        )
        self.accept()
        
    def subject_type_changed(self, i):
        if i == ADDITIONAL_PART:
            self.scan_name_input.setText(self.scan_name + '-new part')
            self.scan_name_input.setReadOnly(True)
            self.is_additional_part = True
        else:
            self.scan_name_input.setText('')
            self.scan_name_input.setReadOnly(False)
            self.is_additional_part = False
