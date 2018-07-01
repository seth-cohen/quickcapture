# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'messagedialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(512, 387)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.text = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.text.setFont(font)
        self.text.setObjectName("text")
        self.verticalLayout.addWidget(self.text)
        self.information_text = QtWidgets.QLabel(Dialog)
        self.information_text.setWordWrap(True)
        self.information_text.setObjectName("information_text")
        self.verticalLayout.addWidget(self.information_text)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.image = QtWidgets.QLabel(Dialog)
        self.image.setMinimumSize(QtCore.QSize(256, 256))
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.image.setObjectName("image")
        self.horizontalLayout.addWidget(self.image)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.no_button = QtWidgets.QPushButton(Dialog)
        self.no_button.setObjectName("no_button")
        self.horizontalLayout_2.addWidget(self.no_button)
        self.button = QtWidgets.QPushButton(Dialog)
        self.button.setDefault(True)
        self.button.setObjectName("button")
        self.horizontalLayout_2.addWidget(self.button)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.text.setText(_translate("Dialog", "TextLabel"))
        self.information_text.setText(_translate("Dialog", "TextLabel"))
        self.image.setText(_translate("Dialog", "TextLabel"))
        self.no_button.setText(_translate("Dialog", "No Thanks"))
        self.button.setText(_translate("Dialog", "Yes"))

