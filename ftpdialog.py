import ftpdialog_auto


class FTPDialog(QDialog, ftpdialog_auto.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
