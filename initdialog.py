import sys
import PyQt5
from PyQt5.QtWidgets import *
import initdialog_auto

class InitDialog(QDialog, initdialog_auto.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
