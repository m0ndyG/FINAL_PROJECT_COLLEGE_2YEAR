import sys
from PyQt6 import QtCore, QtGui, QtWidgets
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class LegalGuide(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.headers = {'user-agent': UserAgent().random}
        self.session = requests.Session()
        self.BASE_URL = 'https://www.zakonrf.info'

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Правовой справочник")

        # Создание боковой панели
        self.side_panel = QtWidgets.QWidget()
        self.side_panel.setFixedWidth(200)  # Установите ширину, которую вы хотите

        # Создание контейнера для центрирования виджетов
        self.container = QtWidgets.QWidget()
        self.container_layout = QtWidgets.QVBoxLayout(self.container)

        self.law_type = QtWidgets.QComboBox()
        self.law_type.addItems(["uk", "gk", "tk", "koap", "konstitucia"])  # Добавьте все виды законов здесь
        self.container_layout.addWidget(self.law_type)

        self.entry = QtWidgets.QTextEdit()
        self.entry.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.WidgetWidth)
        self.container_layout.addWidget(self.entry)

        self.search_button = QtWidgets.QPushButton("Поиск")
        self.search_button.clicked.connect(self.search_law)
        self.container_layout.addWidget(self.search_button)

        self.clear_button = QtWidgets.QPushButton("Очистить")
        self.clear_button.clicked.connect(self.clear_text)
        self.container_layout.addWidget(self.clear_button)

        # Центрирование контейнера в боковой панели
        self.side_layout = QtWidgets.QVBoxLayout(self.side_panel)
        self.side_layout.addWidget(self.container, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # Создание области вывода текста
        self.text = QtWidgets.QTextBrowser()
        self.text.setOpenExternalLinks(True)

        # Размещение боковой панели и области текста в главном окне
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QtWidgets.QHBoxLayout(self.main_widget)
        self.main_layout.addWidget(self.side_panel)
        self.main_layout.addWidget(self.text)

    def search_law(self):
        try:
            self.text.clear()
            law_number = int(self.entry.toPlainText())
            law_type = self.law_type.currentText()

            url = f'{self.BASE_URL}/{law_type}/{law_number}'
            search_request = self.session.get(url, headers=self.headers)

            soup = BeautifulSoup(search_request.content, 'html.parser')

            # Извлекаем название закона
            law_title = soup.find(class_='law-h1').text
            self.text.append(f'Название закона: {law_title}')

            # Извлекаем текст закона
            law_text = soup.find(class_='st-body content-body').text
            self.text.append(f'Текст закона: {law_text}')
        except Exception as e:
            self.text.append(f'Произошла ошибка: {str(e)}')

    def clear_text(self):
        self.text.clear()

def main():
    app = QtWidgets.QApplication(sys.argv)

    guide = LegalGuide()
    guide.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
