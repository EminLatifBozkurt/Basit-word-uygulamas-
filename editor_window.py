from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit, QAction, QFileDialog, QFontDialog, QInputDialog, QMessageBox, QMenuBar
)
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QPalette, QFont
from PyQt5.QtCore import Qt, QFileInfo
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog  


class WordLikeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Word")
        self.setGeometry(100, 100, 800, 600)
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)

        self.create_menu()

        # Başlangıçta açık tema olarak ayarla
        self.dark_mode = False
        self.set_light_theme()

        # Eşleşmeleri kaydetmek için liste
        self.all_cursors = []

        # Tıklama olayını bağla
        self.text_edit.cursorPositionChanged.connect(self.reset_highlight)

    def create_menu(self):
        menubar = self.menuBar()

        # Dosya menüsü
        file_menu = menubar.addMenu("Dosya")
        new_action = QAction("Yeni", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Aç", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Kaydet", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        print_action = QAction("Yazdır", self)
        print_action.triggered.connect(self.print_file)
        file_menu.addAction(print_action)

        # Biçim menüsü
        format_menu = menubar.addMenu("Biçim")
        font_action = QAction("Yazı Tipi", self)
        font_action.triggered.connect(self.choose_font)
        format_menu.addAction(font_action)

        bold_action = QAction("Kalın", self)
        bold_action.triggered.connect(self.make_bold)
        format_menu.addAction(bold_action)

        italic_action = QAction("İtalik", self)
        italic_action.triggered.connect(self.make_italic)
        format_menu.addAction(italic_action)

        underline_action = QAction("Altı Çizili", self)
        underline_action.triggered.connect(self.make_underline)
        format_menu.addAction(underline_action)

        # Düzenle menüsü
        edit_menu = menubar.addMenu("Düzenle")
        undo_action = QAction("Geri Al", self)
        undo_action.triggered.connect(self.text_edit.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Yinele", self)
        redo_action.triggered.connect(self.text_edit.redo)
        edit_menu.addAction(redo_action)

        word_count_action = QAction("Kelime Sayısını Göster", self)
        word_count_action.triggered.connect(self.word_count)
        edit_menu.addAction(word_count_action)

        find_action = QAction("Metin Ara", self)
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)

        # Görünüm menüsü
        view_menu = menubar.addMenu("Görünüm")
        dark_mode_action = QAction("Koyu Tema", self)
        dark_mode_action.triggered.connect(self.set_dark_theme)
        view_menu.addAction(dark_mode_action)

        light_mode_action = QAction("Açık Tema", self)
        light_mode_action.triggered.connect(self.set_light_theme)
        view_menu.addAction(light_mode_action)

    def new_file(self):
        self.text_edit.clear()

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Dosya Aç", "", "Metin Dosyaları (*.txt *.rtf)")
        if file_name:
            with open(file_name, 'r', encoding='utf-8') as f:
                self.text_edit.setPlainText(f.read())

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Dosya Kaydet", "", "Metin Dosyaları (*.txt)")
        if file_name:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())

    def print_file(self):
        printer = QPrinter()
        print_dialog = QPrintDialog(printer, self)

        if print_dialog.exec_() == QPrintDialog.Accepted:
            self.text_edit.print_(printer)

    def choose_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.text_edit.setCurrentFont(font)

    def make_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold)
        self.merge_format(fmt)

    def make_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(True)
        self.merge_format(fmt)

    def make_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(True)
        self.merge_format(fmt)

    def merge_format(self, fmt):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(fmt)
        self.text_edit.mergeCurrentCharFormat(fmt)

    def word_count(self):
        text = self.text_edit.toPlainText()
        word_count = len(text.split())
        char_count = len(text)
        QMessageBox.information(self, "Kelime Sayısı", f"Kelime Sayısı: {word_count}\nKarakter Sayısı: {char_count}")

    def find_text(self):
        text, ok = QInputDialog.getText(self, 'Metin Ara', 'Aramak istediğiniz metni girin:')
        if ok and text:
            cursor = self.text_edit.document().find(text)  # İlk eşleşmeyi bul
            if cursor.isNull():
                QMessageBox.information(self, "Sonuç", "Metin bulunamadı.")
            else:
                count = 0
                self.all_cursors.clear()  # Önceki eşleşmeleri temizle
                while not cursor.isNull():
                    count += 1
                    self.all_cursors.append(cursor)  # Eşleşen metni kaydet
                    cursor = self.text_edit.document().find(text, cursor)  # Sonraki eşleşmeyi bul

                # Tema kontrolüne göre renk seçimi yap
                if self.dark_mode:  # Koyu tema
                    highlight_color = QColor(0, 0, 255)  # Mavi
                else:  # Açık tema
                    highlight_color = QColor(255, 255, 0)  # Sarı

                # Tüm eşleşmeleri işaretle
                for cursor in self.all_cursors:
                    fmt = QTextCharFormat()
                    fmt.setBackground(highlight_color)  # Seçilen arka plan rengi
                    cursor.mergeCharFormat(fmt)

                # Eşleşme sayısını göster
                QMessageBox.information(self, "Sonuç", f"Toplam {count} eşleşme bulundu.")

    def reset_highlight(self):
        """Tıklama sonrası vurguyu sıfırlama"""
        cursor = self.text_edit.textCursor()
        
        # Tıklandığında sadece arka plan rengini sıfırlayalım
        fmt = QTextCharFormat()
        fmt.setBackground(Qt.transparent)  # Arka planı şeffaf yap
        cursor.mergeCharFormat(fmt)
        
        # Yeni vurguları tekrar ayarla
        if self.all_cursors:  # Eğer eşleşme varsa
            for cursor in self.all_cursors:
                fmt = QTextCharFormat()
                fmt.setBackground(QColor(0, 0, 255) if self.dark_mode else QColor(255, 255, 0))  # Mavi veya Sarı
                cursor.mergeCharFormat(fmt)

    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        self.setPalette(dark_palette)

        # Koyu tema için menü renklerini ayarla
        self.menuBar().setStyleSheet("QMenuBar { background-color: #333; color: white; }"
                                     "QMenuBar::item { background-color: #333; color: white; }"
                                     "QMenuBar::item:selected { background-color: #555; }"
                                     "QMenuBar::item:pressed { background-color: #777; }")

        self.dark_mode = True

    def set_light_theme(self):
     light_palette = QPalette()
     light_palette.setColor(QPalette.Window, Qt.white)
     light_palette.setColor(QPalette.WindowText, Qt.black)
     light_palette.setColor(QPalette.Base, Qt.white)
     light_palette.setColor(QPalette.AlternateBase, Qt.lightGray)
     light_palette.setColor(QPalette.ToolTipBase, Qt.white)
     light_palette.setColor(QPalette.ToolTipText, Qt.black)
     light_palette.setColor(QPalette.Text, Qt.black)
     light_palette.setColor(QPalette.Button, Qt.white)
     light_palette.setColor(QPalette.ButtonText, Qt.black)
     light_palette.setColor(QPalette.Highlight, QColor(0, 120, 215))  # Renk düzeltmesi
     light_palette.setColor(QPalette.HighlightedText, Qt.black)

     self.setPalette(light_palette)
     self.menuBar().setStyleSheet("QMenuBar { background-color: #f0f0f0; color: black; }"
                                 "QMenuBar::item { background-color: #f0f0f0; color: black; }"
                                 "QMenuBar::item:selected { background-color: #d0d0d0; }"
                                 "QMenuBar::item:pressed { background-color: #b0b0b0; }")
