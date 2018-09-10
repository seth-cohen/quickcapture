import sys
import PyQt5
import PyQt5.QtWidgets as Qtw
import dialogs.newscandialog_auto as newscandialog_auto

NEW_PRODUCT = 0
ADDITIONAL_PART = 1
ADDITIONAL_ORIENTATION = 2

SKU = 0
PROP = 1
OTHER = 2

PRODUCTION = 0
EXPERIMENT = 1


class NewScanDialog(Qtw.QDialog, newscandialog_auto.Ui_NewScanDialog):
    """The class representing the dialog to initiate new scans

    Attributes:
        scan_name (str): Name of the scan (could be previous name if additional part)
        part_id (str): Manufacturer part id (empty if this is a prop)
        is_additional_part (bool): Whether this subject is the next part
            of a multi-part sku
        scan_notes (str): Notes about the scan
        should_generate_3d_model (bool): Whether the scan source wants to generate
            3d model or just wants silo
        all_scan_ids (list[str]): List of all of the primary scan ids
        is_additional_orientation (bool): Whether this scan should be an 
            additional orientation of the previous (same part)

    """
    def __init__(self, is_first=False, scan_name='', part_id='', all_scan_ids=[]):
        super().__init__()
        self.setupUi(self)
        
        self.scan_name = scan_name
        self.part_id = part_id
        self.is_additional_part = False
        self.scan_notes = ''
        self.should_generate_3d_model = True
        self.all_scan_ids = all_scan_ids
        self.is_additional_orientation = False
        
        if scan_name == '':
            self.scan_name_input.setReadOnly(False)
            self.mfg_part_id_input.setReadOnly(False)
            self.subject_type.model().item(1).setSelectable(False)
            self.subject_type.model().item(2).setSelectable(False)

        self.object_type = 'SKU'
        self.subject_type.currentIndexChanged.connect(self.subject_type_changed)
        self.object_type_input.currentIndexChanged.connect(self.object_type_changed)
        self.start_scan_button.clicked.connect(self.start_scan)
        self.cancel_button.clicked.connect(self.reject)

    def start_scan(self):
        self.scan_name = self.scan_name_input.text()
        self.part_id = self.mfg_part_id_input.text()
        missing_scan_name = self.scan_name == ''
        missing_part_id = self.part_id == '' and self.object_type_input.currentIndex() == SKU

        if missing_scan_name or missing_part_id:
            Qtw.QMessageBox.about(self, 'Error', '{}{}'.format(
                '- Please enter name for scan\n' if missing_scan_name else '',
                '- Please enter Product ID\n' if missing_part_id else '',
            ))
            return

        if (self.is_additional_part == False and self.is_additional_orientation == False
            and (self.scan_name in self.all_scan_ids
                 or self.part_id in self.all_scan_ids)):
            Qtw.QMessageBox.about(
                self,
                'Error: Name in use',
                ('Either the prop name, or sku part id {} is already in use.'
                 ' Perhaps Subject type should be Additional Part,'
                 ' or Additional Orientation. If not please update' 
                 ' the name or part id'.format(self.scan_name))
            )
            return


        if self.subject_type.currentIndex == ADDITIONAL_PART:
            self.scan_name += '(Part {})'.format(self.parts_count)

        self.scan_notes = self.scan_notes_input.toPlainText()
        self.object_type = self.object_type_input.currentText()
        self.should_generate_3d_model = self.generate_3d_model_input.isChecked()
        self.scan_type = self.scan_type_input.currentText()

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
            self.is_additional_orientation = False
        elif i == ADDITIONAL_ORIENTATION:
            self.scan_name_input.setText(self.scan_name)
            self.scan_name_input.setReadOnly(True)
            
            self.mfg_part_id_input.setText(self.part_id)
            self.mfg_part_id_input.setReadOnly(True)

            self.is_additional_part = False
            self.is_additional_orientation = True
        else:
            self.scan_name_input.setText('')
            self.scan_name_input.setReadOnly(False)
            
            self.is_additional_part = False
            self.is_additional_orientation = False

    def object_type_changed(self, i):
        if i == SKU:
            self.part_label.show()
            self.mfg_part_id_input.show()
        else:
            self.part_label.hide()
            self.mfg_part_id_input.hide()
            
