import pathlib

from PyQt5 import QtCore, QtWidgets, QtSvg

from .tfnev_welcomewindow_ui import Ui_WelcomeWindow
from tfne_visualizer import TFNEVMainWindow


class TFNEVWelcomeWindow(QtWidgets.QMainWindow, Ui_WelcomeWindow):
    def __init__(self, *args, **kwargs):
        super(TFNEVWelcomeWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Add TFNEV Logo (placeholder for now)
        self.svg_logo = QtSvg.QSvgWidget(self.centralwidget)
        self.svg_logo.load('./tfnev_welcomewindow/tfnev_placeholder_logo.svg')
        self.svg_logo.setGeometry(QtCore.QRect(10, 10, 180, 180))

        # Connect signals
        self.button_open_backup_dir.clicked.connect(self.select_tfne_backup_folder)

        # Show Window
        self.show()

    def select_tfne_backup_folder(self):
        # Start file dialog to open TFNE Backup directory
        f_dialog = QtWidgets.QFileDialog(self, 'Select TFNE Backup Directory', str(pathlib.Path.home()))
        f_dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        f_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        if f_dialog.exec_() == QtWidgets.QDialog.Accepted:
            backup_dir_path = f_dialog.selectedFiles()[0]
            print("Chosen TFNE backup dir: {}".format(backup_dir_path))
        else:
            print('Aborted File Dialog')
            return

        # Create and show TFNE Visualizer mainwindow, now that the backup dir is chosen. Close Welcome Window
        self.tfnev_mainwindow = TFNEVMainWindow(backup_dir_path, self)
        self.tfnev_mainwindow.show()
        self.close()
