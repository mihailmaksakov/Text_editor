import sys
import atexit
from PyQt5 import QtWidgets, QtGui, QtCore, uic


class TextEditor(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("text_editor_main_window.ui", self)
        self.setup_ui()
        self.connect_events()
        self.current_file = CurrentFile()

    def connect_events(self):
        self.ui.action_open.triggered.connect(self.open_file_event)

    # file operation events procession
    def open_file_event(self):
        self.open_file_name_dialog()

    # general-purpose functions
    def setup_ui(self):
        pass

    def open_file_name_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
                        self, "Open file to edit", "",
                        "Text files (*);;Text files (*.txt)", options=options
        )
        if file_name:
            self.current_file.open(file_name)
            if self.current_file.is_opened():
                self.ui.textEdit.setText(self.current_file.get_text())

    def cleanup(self):
        if self.current_file:
            self.current_file.cleanup()

class CurrentFile:

    def __init__(self):
        self._modified_ = False
        self._opened_ = False
        self._full_file_name_ = ''
        self._file_object_ = None

    def cleanup(self):
        if self.is_opened():
            self.close()

    def close(self):
        if self.is_opened():
            self._file_object_.close()
            self._file_object_ = None
            self._modified_ = False
            self._opened_ = False
            self._full_file_name_ = ''

    def save(self, text):
        pass

    def open(self, file_name):

        try:
            self._file_object_ = open(file_name, mode='r+')
        except OSError as error:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage(f'Error opening file {file_name}: {error.errno}!')
            return

        self._full_file_name_ = file_name
        self._opened_ = True
        self.set_unmodified()

    def get_text(self):
        if self.is_opened() and self._file_object_.readable():
            return self._file_object_.read()
        else:
            return 'Error: file is not opened!'

    def set_modified(self):
        self._modified_ = True

    def set_unmodified(self):
        self._modified_ = False

    def is_modified(self):
        return self._modified_

    def is_opened(self):
        return self._opened_


app = QtWidgets.QApplication([])

win = TextEditor()
atexit.register(win.cleanup)

win.show()

sys.exit(app.exec())