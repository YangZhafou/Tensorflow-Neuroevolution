#!python3

import sys

from PyQt5 import QtWidgets

from tfne_visualizer import TFNEVWelcomeWindow

if __name__ == '__main__':
    tfnev = QtWidgets.QApplication(sys.argv)
    tfnev_welcomewindow = TFNEVWelcomeWindow()
    tfnev.exec()
