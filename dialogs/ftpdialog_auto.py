# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ftpdialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FTPDialog(object):
    def setupUi(self, FTPDialog):
        FTPDialog.setObjectName("FTPDialog")
        FTPDialog.resize(627, 763)
        FTPDialog.setStyleSheet("")
        self.verticalLayout = QtWidgets.QVBoxLayout(FTPDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontal_ftp_summary_layout = QtWidgets.QHBoxLayout()
        self.horizontal_ftp_summary_layout.setObjectName("horizontal_ftp_summary_layout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_9 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_3.addWidget(self.label_9)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_10 = QtWidgets.QLabel(FTPDialog)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_7.addWidget(self.label_10)
        self.label_13 = QtWidgets.QLabel(FTPDialog)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_7.addWidget(self.label_13)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.line_3 = QtWidgets.QFrame(FTPDialog)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_3.addWidget(self.line_3)
        self.label_7 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_3.addWidget(self.label_7)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.host_label = QtWidgets.QLabel(FTPDialog)
        self.host_label.setObjectName("host_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.host_label)
        self.host = QtWidgets.QLineEdit(FTPDialog)
        self.host.setFocusPolicy(QtCore.Qt.NoFocus)
        self.host.setReadOnly(True)
        self.host.setObjectName("host")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.host)
        self.username_label = QtWidgets.QLabel(FTPDialog)
        self.username_label.setObjectName("username_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.username_label)
        self.username = QtWidgets.QLineEdit(FTPDialog)
        self.username.setFocusPolicy(QtCore.Qt.NoFocus)
        self.username.setReadOnly(True)
        self.username.setObjectName("username")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.username)
        self.verticalLayout_3.addLayout(self.formLayout)
        self.horizontal_ftp_summary_layout.addLayout(self.verticalLayout_3)
        self.vertical_logo_layout = QtWidgets.QVBoxLayout()
        self.vertical_logo_layout.setObjectName("vertical_logo_layout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vertical_logo_layout.addItem(spacerItem1)
        self.logo = QtWidgets.QLabel(FTPDialog)
        self.logo.setMinimumSize(QtCore.QSize(128, 128))
        self.logo.setMaximumSize(QtCore.QSize(128, 128))
        self.logo.setObjectName("logo")
        self.vertical_logo_layout.addWidget(self.logo)
        self.horizontal_ftp_summary_layout.addLayout(self.vertical_logo_layout)
        self.verticalLayout.addLayout(self.horizontal_ftp_summary_layout)
        self.line = QtWidgets.QFrame(FTPDialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.progress_label = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.progress_label.setFont(font)
        self.progress_label.setObjectName("progress_label")
        self.verticalLayout.addWidget(self.progress_label)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(FTPDialog)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.progress_1 = QtWidgets.QProgressBar(FTPDialog)
        self.progress_1.setMinimumSize(QtCore.QSize(0, 0))
        self.progress_1.setProperty("value", 0)
        self.progress_1.setTextVisible(True)
        self.progress_1.setObjectName("progress_1")
        self.horizontalLayout_2.addWidget(self.progress_1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(FTPDialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.progress_2 = QtWidgets.QProgressBar(FTPDialog)
        self.progress_2.setProperty("value", 0)
        self.progress_2.setObjectName("progress_2")
        self.horizontalLayout_4.addWidget(self.progress_2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_4 = QtWidgets.QLabel(FTPDialog)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        self.progress_3 = QtWidgets.QProgressBar(FTPDialog)
        self.progress_3.setProperty("value", 0)
        self.progress_3.setObjectName("progress_3")
        self.horizontalLayout_5.addWidget(self.progress_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(FTPDialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.progress_4 = QtWidgets.QProgressBar(FTPDialog)
        self.progress_4.setProperty("value", 0)
        self.progress_4.setObjectName("progress_4")
        self.horizontalLayout_3.addWidget(self.progress_4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.line_2 = QtWidgets.QFrame(FTPDialog)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.progress_label_2 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.progress_label_2.setFont(font)
        self.progress_label_2.setObjectName("progress_label_2")
        self.verticalLayout_5.addWidget(self.progress_label_2)
        self.formLayout_3 = QtWidgets.QFormLayout()
        self.formLayout_3.setObjectName("formLayout_3")
        self.label_6 = QtWidgets.QLabel(FTPDialog)
        self.label_6.setObjectName("label_6")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.label_12 = QtWidgets.QLabel(FTPDialog)
        self.label_12.setObjectName("label_12")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_12)
        self.label_14 = QtWidgets.QLabel(FTPDialog)
        self.label_14.setObjectName("label_14")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_14)
        self.label_15 = QtWidgets.QLabel(FTPDialog)
        self.label_15.setObjectName("label_15")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_15)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.ftp_progress_1 = QtWidgets.QProgressBar(FTPDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftp_progress_1.sizePolicy().hasHeightForWidth())
        self.ftp_progress_1.setSizePolicy(sizePolicy)
        self.ftp_progress_1.setMinimumSize(QtCore.QSize(375, 0))
        self.ftp_progress_1.setMaximumSize(QtCore.QSize(375, 16777215))
        self.ftp_progress_1.setProperty("value", 0)
        self.ftp_progress_1.setObjectName("ftp_progress_1")
        self.horizontalLayout_8.addWidget(self.ftp_progress_1)
        self.label_8 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_8.addWidget(self.label_8)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem2)
        self.speed_1 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.speed_1.setFont(font)
        self.speed_1.setObjectName("speed_1")
        self.horizontalLayout_8.addWidget(self.speed_1)
        self.speed_unit_1 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.speed_unit_1.setFont(font)
        self.speed_unit_1.setObjectName("speed_unit_1")
        self.horizontalLayout_8.addWidget(self.speed_unit_1)
        self.formLayout_3.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_8)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.ftp_progress_2 = QtWidgets.QProgressBar(FTPDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftp_progress_2.sizePolicy().hasHeightForWidth())
        self.ftp_progress_2.setSizePolicy(sizePolicy)
        self.ftp_progress_2.setMinimumSize(QtCore.QSize(375, 0))
        self.ftp_progress_2.setMaximumSize(QtCore.QSize(375, 16777215))
        self.ftp_progress_2.setProperty("value", 0)
        self.ftp_progress_2.setObjectName("ftp_progress_2")
        self.horizontalLayout_9.addWidget(self.ftp_progress_2)
        self.label_16 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.horizontalLayout_9.addWidget(self.label_16)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem3)
        self.speed_2 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.speed_2.setFont(font)
        self.speed_2.setObjectName("speed_2")
        self.horizontalLayout_9.addWidget(self.speed_2)
        self.speed_unit_2 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.speed_unit_2.setFont(font)
        self.speed_unit_2.setObjectName("speed_unit_2")
        self.horizontalLayout_9.addWidget(self.speed_unit_2)
        self.formLayout_3.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.ftp_progress_3 = QtWidgets.QProgressBar(FTPDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftp_progress_3.sizePolicy().hasHeightForWidth())
        self.ftp_progress_3.setSizePolicy(sizePolicy)
        self.ftp_progress_3.setMinimumSize(QtCore.QSize(375, 0))
        self.ftp_progress_3.setMaximumSize(QtCore.QSize(375, 16777215))
        self.ftp_progress_3.setProperty("value", 0)
        self.ftp_progress_3.setObjectName("ftp_progress_3")
        self.horizontalLayout_10.addWidget(self.ftp_progress_3)
        self.label_18 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.horizontalLayout_10.addWidget(self.label_18)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem4)
        self.speed_3 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.speed_3.setFont(font)
        self.speed_3.setObjectName("speed_3")
        self.horizontalLayout_10.addWidget(self.speed_3)
        self.speed_unit_3 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.speed_unit_3.setFont(font)
        self.speed_unit_3.setObjectName("speed_unit_3")
        self.horizontalLayout_10.addWidget(self.speed_unit_3)
        self.formLayout_3.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_10)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.ftp_progress_4 = QtWidgets.QProgressBar(FTPDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftp_progress_4.sizePolicy().hasHeightForWidth())
        self.ftp_progress_4.setSizePolicy(sizePolicy)
        self.ftp_progress_4.setMinimumSize(QtCore.QSize(375, 0))
        self.ftp_progress_4.setMaximumSize(QtCore.QSize(375, 16777215))
        self.ftp_progress_4.setProperty("value", 0)
        self.ftp_progress_4.setObjectName("ftp_progress_4")
        self.horizontalLayout_11.addWidget(self.ftp_progress_4)
        self.label_20 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_20.setFont(font)
        self.label_20.setObjectName("label_20")
        self.horizontalLayout_11.addWidget(self.label_20)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem5)
        self.speed_4 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.speed_4.setFont(font)
        self.speed_4.setObjectName("speed_4")
        self.horizontalLayout_11.addWidget(self.speed_4)
        self.speed_unit_4 = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.speed_unit_4.setFont(font)
        self.speed_unit_4.setObjectName("speed_unit_4")
        self.horizontalLayout_11.addWidget(self.speed_unit_4)
        self.formLayout_3.setLayout(3, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_11)
        self.verticalLayout_5.addLayout(self.formLayout_3)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem6)
        self.existing_dir = QtWidgets.QPushButton(FTPDialog)
        self.existing_dir.setObjectName("existing_dir")
        self.horizontalLayout_6.addWidget(self.existing_dir)
        self.verticalLayout_5.addLayout(self.horizontalLayout_6)
        self.verticalLayout.addLayout(self.verticalLayout_5)
        self.status_label = QtWidgets.QLabel(FTPDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.status_label.setFont(font)
        self.status_label.setObjectName("status_label")
        self.verticalLayout.addWidget(self.status_label)
        self.status_log = QtWidgets.QTextEdit(FTPDialog)
        self.status_log.setFocusPolicy(QtCore.Qt.NoFocus)
        self.status_log.setReadOnly(True)
        self.status_log.setObjectName("status_log")
        self.verticalLayout.addWidget(self.status_log)
        self.dialog_buttons = QtWidgets.QDialogButtonBox(FTPDialog)
        self.dialog_buttons.setOrientation(QtCore.Qt.Horizontal)
        self.dialog_buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.dialog_buttons.setObjectName("dialog_buttons")
        self.verticalLayout.addWidget(self.dialog_buttons)

        self.retranslateUi(FTPDialog)
        self.dialog_buttons.accepted.connect(FTPDialog.accept)
        self.dialog_buttons.rejected.connect(FTPDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FTPDialog)
        FTPDialog.setTabOrder(self.host, self.username)
        FTPDialog.setTabOrder(self.username, self.status_log)

    def retranslateUi(self, FTPDialog):
        _translate = QtCore.QCoreApplication.translate
        FTPDialog.setWindowTitle(_translate("FTPDialog", "File Copy and Transfer"))
        self.label_9.setText(_translate("FTPDialog", "Summary"))
        self.label_10.setText(_translate("FTPDialog", "Transfer"))
        self.label_13.setText(_translate("FTPDialog", " Files to Wayfair Next Scanning Service?"))
        self.label_7.setText(_translate("FTPDialog", "FTP Details"))
        self.host_label.setText(_translate("FTPDialog", "FTP Host: "))
        self.username_label.setText(_translate("FTPDialog", "Username: "))
        self.logo.setText(_translate("FTPDialog", "TextLabel"))
        self.progress_label.setText(_translate("FTPDialog", "Copy Progress"))
        self.label.setText(_translate("FTPDialog", "Camera 1: "))
        self.label_3.setText(_translate("FTPDialog", "Camera 2: "))
        self.label_4.setText(_translate("FTPDialog", "Camera 3: "))
        self.label_2.setText(_translate("FTPDialog", "Camera 4: "))
        self.progress_label_2.setText(_translate("FTPDialog", "File Transfer Progress"))
        self.label_6.setText(_translate("FTPDialog", "Camera 1: "))
        self.label_12.setText(_translate("FTPDialog", "Camera 2: "))
        self.label_14.setText(_translate("FTPDialog", "Camera 3: "))
        self.label_15.setText(_translate("FTPDialog", "Camera 4: "))
        self.label_8.setText(_translate("FTPDialog", "Speed:"))
        self.speed_1.setText(_translate("FTPDialog", "0"))
        self.speed_unit_1.setText(_translate("FTPDialog", "kbps"))
        self.label_16.setText(_translate("FTPDialog", "Speed:"))
        self.speed_2.setText(_translate("FTPDialog", "0"))
        self.speed_unit_2.setText(_translate("FTPDialog", "kbps"))
        self.label_18.setText(_translate("FTPDialog", "Speed:"))
        self.speed_3.setText(_translate("FTPDialog", "0"))
        self.speed_unit_3.setText(_translate("FTPDialog", "kbps"))
        self.label_20.setText(_translate("FTPDialog", "Speed:"))
        self.speed_4.setText(_translate("FTPDialog", "0"))
        self.speed_unit_4.setText(_translate("FTPDialog", "kbps"))
        self.existing_dir.setText(_translate("FTPDialog", "FTP Existing Directory"))
        self.status_label.setText(_translate("FTPDialog", "Status"))

