import PyQt5.QtWidgets as Qtw
import PyQt5.QtCore as Qtc
import dialogs.messagedialog_auto as msgdialog_auto


class MessageDialog(Qtw.QDialog, msgdialog_auto.Ui_Dialog):
    """Generic message box dialog containing center image

    Adds more versatility to the built in QMessageBox which doesn't
    have that much capability and has troubles with sizing

    """
    def __init__(self, button_text, title, text, information_text, image, is_choice=False, no_button_text=None):
        super().__init__()
        self.setupUi(self)

        self.button.setText(button_text)
        if no_button_text is not None:
            self.no_button.setText(no_button_text)
            
        self.setWindowTitle(title)
        self.text.setText(text)
        self.information_text.setText(information_text)
        self.image.setPixmap(image.scaled(self.image.width(), self.image.height(), Qtc.Qt.KeepAspectRatio))

        if not is_choice:
            self.no_button.setHidden(True)

        self.button.clicked.connect(self.accept)
        self.no_button.clicked.connect(self.reject)
