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
    def __init__(self, is_first=False, scan_name='', part_id=''):
        super().__init__()
        self.setupUi(self)
        
        self.scan_name = scan_name
        self.part_id = part_id
        self.is_additional_part = False
        self.scan_notes = ''
        self.should_generate_3d_model = True
        
        if scan_name == '':
            self.scan_name_input.setReadOnly(False)
            self.mfg_part_id_input.setReadOnly(False)
            self.subject_type.model().item(1).setSelectable(False)

        self.scan_type = 'SKU'
        self.subject_type.currentIndexChanged.connect(self.subject_type_changed)
        self.scan_type_input.currentIndexChanged.connect(self.scan_type_changed)
        self.start_scan_button.clicked.connect(self.start_scan)
        self.cancel_button.clicked.connect(self.reject)

    def start_scan(self):
        self.scan_name = self.scan_name_input.text()
        self.part_id = self.mfg_part_id_input.text()
        missing_scan_name = self.scan_name == ''
        missing_part_id = self.part_id == '' and self.scan_type_input.currentIndex() == SKU

        if missing_scan_name or missing_part_id:
            Qtw.QMessageBox.about(self, 'Error', '{}{}'.format(
                '- Please enter name for scan\n' if missing_scan_name else '',
                '- Please enter Product ID\n' if missing_part_id else '',
            ))
            return

        if self.subject_type.currentIndex == ADDITIONAL_PART:
            self.scan_name += '(Part {})'.format(self.parts_count)

        self.scan_notes = self.scan_notes_input.toPlainText()
        self.scan_type = self.scan_type_input.currentText()
        self.should_generate_3d_model = self.generate_3d_model_input.isChecked()

        Qtw.QMessageBox.warning(
            self,
            'Prepare For Scan',
            'Before clicking `OK`, ensure that camera settings are correct and in focus. Then place the object to scan on the turntable.'
        )
        self.accept()
        
    def subject_type_changed(self, i):
        if i == ADDITIONAL_PART:
            self.scan_name_input.setText(self.scan_name)
            self.scan_name_input.setReadOnly(True)
            
            self.mfg_part_id_input.setText(self.part_id)
            self.mfg_part_id_input.setReadOnly(True)

            self.is_additional_part = True
        else:
            self.scan_name_input.setText('')
            self.scan_name_input.setReadOnly(False)
            self.is_additional_part = False

    def scan_type_changed(self, i):
        if i == SKU:
            self.part_label.show()
            self.mfg_part_id_input.show()
        else:
            self.part_label.hide()
            self.mfg_part_id_input.hide()
            
