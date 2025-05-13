import sys
from PyQt5.QtWidgets import QApplication
from editor_window import WordLikeEditor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordLikeEditor()
    window.show()
    sys.exit(app.exec_())