# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newscandialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NewScanDialog(object):
    def setupUi(self, NewScanDialog):
        NewScanDialog.setObjectName("NewScanDialog")
        NewScanDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        NewScanDialog.resize(416, 227)
        self.verticalLayout = QtWidgets.QVBoxLayout(NewScanDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scan_type = QtWidgets.QComboBox(NewScanDialog)
        self.scan_type.setObjectName("scan_type")
        self.scan_type.addItem("")
        self.scan_type.addItem("")
        self.verticalLayout.addWidget(self.scan_type)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(NewScanDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.scan_name_input = QtWidgets.QLineEdit(NewScanDialog)
        self.scan_name_input.setObjectName("scan_name_input")
        self.horizontalLayout.addWidget(self.scan_name_input)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.cancel_button = QtWidgets.QPushButton(NewScanDialog)
        self.cancel_button.setObjectName("cancel_button")
        self.horizontalLayout_2.addWidget(self.cancel_button)
        self.start_scan_button = QtWidgets.QPushButton(NewScanDialog)
        self.start_scan_button.setAutoDefault(True)
        self.start_scan_button.setDefault(True)
        self.start_scan_button.setObjectName("start_scan_button")
        self.horizontalLayout_2.addWidget(self.start_scan_button)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(NewScanDialog)
        QtCore.QMetaObject.connectSlotsByName(NewScanDialog)
        NewScanDialog.setTabOrder(self.scan_name_input, self.start_scan_button)
        NewScanDialog.setTabOrder(self.start_scan_button, self.scan_type)
        NewScanDialog.setTabOrder(self.scan_type, self.cancel_button)

    def retranslateUi(self, NewScanDialog):
        _translate = QtCore.QCoreApplication.translate
        NewScanDialog.setWindowTitle(_translate("NewScanDialog", "Set Scanning Details"))
        self.scan_type.setCurrentText(_translate("NewScanDialog", "Scan New Subject"))
        self.scan_type.setItemText(0, _translate("NewScanDialog", "Scan New Subject"))
        self.scan_type.setItemText(1, _translate("NewScanDialog", "Scan Additional Part (multipart subject)"))
        self.label.setText(_translate("NewScanDialog", "Name of Scan: "))
        self.scan_name_input.setPlaceholderText(_translate("NewScanDialog", "Enter Name "))
        self.cancel_button.setText(_translate("NewScanDialog", "Cancel"))
        self.start_scan_button.setText(_translate("NewScanDialog", "Start Scan"))

