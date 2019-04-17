import sys
from PyQt5.QtWidgets import QApplication
from pylem.controller.main import Main


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if app is None:
        app = QApplication(sys.argv)
    main = Main(app)
    app.exec()
