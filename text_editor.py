import os
import sys
import atexit
from PyQt5 import QtWidgets, QtGui, QtCore, uic

main_window_caption = 'Mike\'s text editor'
ui_file = "text_editor_main_window.ui"


class TextEditor(QtWidgets.QMainWindow):

    def __init__(self):

        super().__init__()
        self.ui = uic.loadUi(ui_file, self)
        self.setup_ui()
        self.connect_events()
        self.current_file = CurrentFile()

    def connect_events(self):

        self.ui.action_open.triggered.connect(self.open_file_event)
        self.ui.action_new.triggered.connect(self.new_file_event)
        self.ui.action_save.triggered.connect(self.save_file_event)
        self.ui.action_save_as.triggered.connect(self.save_as_file_event)

        self.ui.textEdit.textChanged.connect(self.text_modified)

    # text editing procession
    def text_modified(self):
        self.current_file.set_modified()
        self.toggle_modification(True)

    # file operation events procession
    def open_file_event(self):
        if self.check_modification():
            self.open_file_name_dialog()

    def new_file_event(self):
        if self.check_modification():
            self.current_file.cleanup()
            self.set_new_file()

    def save_file_event(self):
        if self.current_file.is_opened():
            self.current_file.save(self.get_text())
        else:
            self.save_file_dialog()

    def save_as_file_event(self):
        self.save_file_dialog()

    # general-purpose functions
    def setup_ui(self):
        pass

    def get_text(self):
        return self.ui.textEdit.toPlainText()

    def toggle_modification(self, modification):
        self.ui.setWindowTitle(f'{main_window_caption}{" * " if modification else ""}')

    def check_modification(self):

        if self.current_file.is_modified():
            question_message = QtWidgets.QMessageBox
            reply = question_message.question(self, 'Warning!', "File was modified, are you sure to discard changes?",
                                              question_message.Yes | question_message.No, question_message.No)
            if reply == question_message.No:
                return False

        return True

    def set_new_file(self):
        self.current_file = CurrentFile()
        self.toggle_modification(False)

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

    def save_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save file", self.current_file.get_file_name(),
            "Text files (*);;Text files (*.txt)", options=options
        )
        if file_name:
            self.current_file.save(self.get_text(), file_name)

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

    def save(self, text, file_name=''):

        if not file_name:
            file_name = self._full_file_name_

        if not self.is_opened():
            self.open(file_name, True)

        if not self.is_opened():
            return

        if self._file_object_.writable():
            try:
                self._file_object_.write(text)
            except OSError as error:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage(f'Error writing file {file_name}: {error.errno}!')
                return
        else:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage(f'Can not write to file {file_name}!')
            return

        self._full_file_name_ = file_name

    def open(self, file_name, new_file = False):

        if os.path.isfile(file_name):
            file_open_mode = 'r+'
        else:
            file_open_mode = 'x'

        try:
            self._file_object_ = open(file_name, mode=file_open_mode)
        except OSError as error:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage(f'Error opening file {file_name}: {error.errno}!')
            return

        self._full_file_name_ = file_name
        self._opened_ = True
        if not new_file:
            self.set_unmodified()

    def get_text(self):
        if self.is_opened() and self._file_object_.readable():
            return self._file_object_.read()
        else:
            return 'Error: file is not opened!'

    def get_file_name(self):
        return self._full_file_name_

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
