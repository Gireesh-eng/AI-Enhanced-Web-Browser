import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import BrowserApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = BrowserApp()
    main_window.show()
    sys.exit(app.exec_())
