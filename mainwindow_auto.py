# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(485, 422)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.lineEdit = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_8.addWidget(self.lineEdit)
        self.pushButton = QtWidgets.QPushButton(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_8.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_6.setContentsMargins(-1, -1, -1, 3)
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.thumbnail_3 = QtWidgets.QLabel(self.centralWidget)
        self.thumbnail_3.setMinimumSize(QtCore.QSize(128, 128))
        self.thumbnail_3.setWordWrap(True)
        self.thumbnail_3.setObjectName("thumbnail_3")
        self.gridLayout.addWidget(self.thumbnail_3, 1, 0, 1, 1)
        self.thumbnail_4 = QtWidgets.QLabel(self.centralWidget)
        self.thumbnail_4.setMinimumSize(QtCore.QSize(128, 128))
        self.thumbnail_4.setWordWrap(True)
        self.thumbnail_4.setObjectName("thumbnail_4")
        self.gridLayout.addWidget(self.thumbnail_4, 1, 1, 1, 1)
        self.thumbnail_2 = QtWidgets.QLabel(self.centralWidget)
        self.thumbnail_2.setMinimumSize(QtCore.QSize(128, 128))
        self.thumbnail_2.setWordWrap(True)
        self.thumbnail_2.setObjectName("thumbnail_2")
        self.gridLayout.addWidget(self.thumbnail_2, 0, 1, 1, 1)
        self.thumbnail_1 = QtWidgets.QLabel(self.centralWidget)
        self.thumbnail_1.setMinimumSize(QtCore.QSize(128, 128))
        self.thumbnail_1.setWordWrap(True)
        self.thumbnail_1.setObjectName("thumbnail_1")
        self.gridLayout.addWidget(self.thumbnail_1, 0, 0, 1, 1)
        self.horizontalLayout_6.addLayout(self.gridLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.camera_counts = QtWidgets.QGroupBox(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_counts.sizePolicy().hasHeightForWidth())
        self.camera_counts.setSizePolicy(sizePolicy)
        self.camera_counts.setObjectName("camera_counts")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.camera_counts)
        self.verticalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.camera_counts)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.image_count_1 = QtWidgets.QLCDNumber(self.camera_counts)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.image_count_1.setFont(font)
        self.image_count_1.setAutoFillBackground(False)
        self.image_count_1.setStyleSheet("QLCDNumber{\n"
"    color: rgb(255, 89, 242);    \n"
"    background-color: rgb(0, 85, 0);\n"
"}")
        self.image_count_1.setSmallDecimalPoint(False)
        self.image_count_1.setObjectName("image_count_1")
        self.horizontalLayout.addWidget(self.image_count_1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.camera_counts)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.image_count_2 = QtWidgets.QLCDNumber(self.camera_counts)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.image_count_2.setFont(font)
        self.image_count_2.setAutoFillBackground(False)
        self.image_count_2.setStyleSheet("QLCDNumber{\n"
"    color: rgb(255, 89, 242);    \n"
"    background-color: rgb(0, 85, 0);\n"
"}")
        self.image_count_2.setSmallDecimalPoint(False)
        self.image_count_2.setObjectName("image_count_2")
        self.horizontalLayout_2.addWidget(self.image_count_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.camera_counts)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.image_count_3 = QtWidgets.QLCDNumber(self.camera_counts)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.image_count_3.setFont(font)
        self.image_count_3.setAutoFillBackground(False)
        self.image_count_3.setStyleSheet("QLCDNumber{\n"
"    color: rgb(255, 89, 242);    \n"
"    background-color: rgb(0, 85, 0);\n"
"}")
        self.image_count_3.setSmallDecimalPoint(False)
        self.image_count_3.setObjectName("image_count_3")
        self.horizontalLayout_3.addWidget(self.image_count_3)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.camera_counts)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.image_count_4 = QtWidgets.QLCDNumber(self.camera_counts)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.image_count_4.setFont(font)
        self.image_count_4.setAutoFillBackground(False)
        self.image_count_4.setStyleSheet("QLCDNumber{\n"
"    color: rgb(255, 89, 242);    \n"
"    background-color: rgb(0, 85, 0);\n"
"}")
        self.image_count_4.setSmallDecimalPoint(False)
        self.image_count_4.setObjectName("image_count_4")
        self.horizontalLayout_4.addWidget(self.image_count_4)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.verticalLayout_2.addWidget(self.camera_counts)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.start_button = QtWidgets.QPushButton(self.centralWidget)
        self.start_button.setObjectName("start_button")
        self.verticalLayout_2.addWidget(self.start_button)
        self.inc_button = QtWidgets.QPushButton(self.centralWidget)
        self.inc_button.setObjectName("inc_button")
        self.verticalLayout_2.addWidget(self.inc_button)
        self.horizontalLayout_6.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "WayfairNext - Quick Capture"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Enter Scan Name"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.thumbnail_3.setText(_translate("MainWindow", "Camera 3 Preview"))
        self.thumbnail_4.setText(_translate("MainWindow", "Camera 4 Preview"))
        self.thumbnail_2.setText(_translate("MainWindow", "Camera 2 Preview"))
        self.thumbnail_1.setText(_translate("MainWindow", "Camera 1 Preview"))
        self.camera_counts.setTitle(_translate("MainWindow", "Photos Taken"))
        self.label.setText(_translate("MainWindow", "Camera 1:"))
        self.label_2.setText(_translate("MainWindow", "Camera 2:"))
        self.label_3.setText(_translate("MainWindow", "Camera 3:"))
        self.label_4.setText(_translate("MainWindow", "Camera 4:"))
        self.start_button.setText(_translate("MainWindow", "Start"))
        self.inc_button.setText(_translate("MainWindow", "Increment"))

