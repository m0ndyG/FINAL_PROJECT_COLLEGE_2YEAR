import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QTextBrowser, QDialog, QLabel
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QPainter, QPainterPath, QPen, QColor
from PyQt6.QtCore import Qt, QRectF
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from PyQt5.QtCore import Qt
import nltk 
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
import os

class RoundButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(50, 30)  # Уменьшаем размер кнопки

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)  # Уменьшаем радиус скругления 
        painter.fillPath(path, QColor('white'))
        painter.setPen(QPen(QColor('blue'), 1))
        painter.drawPath(path)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class LegalGuide(QMainWindow):
    def __init__(self):
        super().__init__()

        self.headers = {'user-agent': UserAgent().random}
        self.session = requests.Session()
        self.BASE_URL = 'https://www.zakonrf.info'
        self.law_type = ''  # Переменная для хранения выбранного типа закона

        self.initUI()
    
    def load_stylesheet(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        css_file = os.path.join(current_dir, 'styles.css')
        with open(css_file, 'r') as f:
            self.setStyleSheet(f.read())


    def initUI(self):
        self.setWindowTitle("Правовой справочник")
        self.setFont(QFont('Segoe UI', 10))
        self.setGeometry(100, 100, 800, 600)

        # Главный виджет и главный макет
        centralWidget = QWidget(self)
        mainLayout = QHBoxLayout(centralWidget)

        # Первая боковая панель для выбора типа закона
        lawTypePanel = QWidget()
        lawTypeLayout = QVBoxLayout(lawTypePanel)
        lawTypePanel.setFixedWidth(150)
        lawTypePanel.setStyleSheet("background-color: #D9D9D9")

        lawTypeLabel = QLabel("Выберите вид закона")
        lawTypeLayout.addWidget(lawTypeLabel)

        # Кнопки для выбора типа закона
        self.btnUK = RoundButton('УК', self)
        self.btnTK = RoundButton('ТК', self)
        self.btnGK = RoundButton('ГК', self)
        self.btnKOAP = RoundButton('КОАП', self)
        self.btnKonstitucia = RoundButton('Конституция', self)
        self.moreLawsButton = RoundButton('...', self)

        # Добавление кнопок в первую боковую панель
        lawTypeLayout.addWidget(self.btnUK)
        lawTypeLayout.addWidget(self.btnTK)
        lawTypeLayout.addWidget(self.btnGK)
        lawTypeLayout.addWidget(self.btnKOAP)
        lawTypeLayout.addWidget(self.btnKonstitucia)
        lawTypeLayout.addWidget(self.moreLawsButton)
        lawTypeLayout.addStretch(1)

        # Вторая боковая панель для поиска по номеру закона
        searchPanel = QWidget()
        searchLayout = QVBoxLayout(searchPanel)
        searchPanel.setFixedWidth(200)
        searchPanel.setStyleSheet("background-color: #F4F4F4")

        searchLabel = QLabel("Введите номер закона")
        searchLayout.addWidget(searchLabel)

        # Поле ввода для номера закона
        self.lawNumberEntry = QLineEdit(self)
        searchLayout.addWidget(self.lawNumberEntry)

        # Кнопка поиска
        searchButton = RoundButton('Поиск', self)
        searchButton.clicked.connect(self.searchLaw)
        searchLayout.addWidget(searchButton)

        # Область для отображения текста закона
        self.lawText = QTextBrowser(self)
        searchLayout.addWidget(self.lawText)

        # Добавление боковых панелей в главный макет
        mainLayout.addWidget(lawTypePanel)
        mainLayout.addWidget(searchPanel)



        # Область для отображения текста закона
        self.lawText = QTextBrowser(self)
        searchLayout.addWidget(self.lawText)  # Добавляем область текста в конец макета

        # Добавление боковых панелей и текстового поля в главный макет
        mainLayout.addWidget(lawTypePanel)
        mainLayout.addWidget(searchPanel)
        mainLayout.addWidget(self.lawText)

        self.setCentralWidget(centralWidget)

        # Сигналы и слоты для кнопок
        self.btnUK.clicked.connect(lambda: self.lawTypeSelected('uk'))
        self.btnTK.clicked.connect(lambda: self.lawTypeSelected('tk'))
        self.btnGK.clicked.connect(lambda: self.lawTypeSelected('gk'))
        self.btnKOAP.clicked.connect(lambda: self.lawTypeSelected('koap'))
        self.btnKonstitucia.clicked.connect(lambda: self.lawTypeSelected('konstitucia'))
        self.moreLawsButton.clicked.connect(self.showMoreLawsDialog)

        # Добавление горячей клавиши Enter для поиска
        QShortcut(QKeySequence(Qt.Key.Key_Return), self, self.searchLaw)

        self.load_stylesheet()
        
    def lawTypeSelected(self, law_type):
        self.law_type = law_type
        self.lawText.append(f"Выбран тип закона: {self.law_type.upper()}")

    def showMoreLawsDialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите тип закона")
        dialogLayout = QVBoxLayout(dialog)

        # Здесь вы можете добавить кнопки для дополнительных типов законов
        # Например:
        btnZK = RoundButton('ЗК', dialog)
        btnZK.clicked.connect(lambda: self.lawTypeSelected('zk'))
        dialogLayout.addWidget(btnZK)

        dialog.exec()

    def searchLaw(self):
        law_number = self.lawNumberEntry.text()
        if not law_number.isdigit():
            self.lawText.append('Пожалуйста, введите корректный номер закона.')
            return

        try:
            self.lawText.clear()
            url = f'{self.BASE_URL}/{self.law_type}/{law_number}'
            response = self.session.get(url, headers=self.headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                law_title_element = soup.find(class_='law-h1')
                law_text_element = soup.find(class_='st-body content-body')

                law_title = law_title_element.text if law_title_element else 'Название закона не найдено.'
                law_text = law_text_element.text if law_text_element else 'Текст закона не найден.'

                # Разбиваем текст названия закона на предложения
                sentences = sent_tokenize(law_title)

                # Берем первое предложение (номер статьи)
                first_sentence = sentences[0]

                # Остальные предложения (название статьи) объединяем в строку с новыми строками между ними
                other_sentences = '\n'.join(sentences[1:])

                # Добавляем названия закона в текстовый виджет
                self.lawText.append(f'<b style="font-size: 14pt;">{first_sentence}</b><br>\n\n<b style="font-size: 14pt;">{other_sentences}</b><br>\n\n<br>\n{law_text}')
            else:
                self.lawText.append('Закон не найден или ошибка сервера.')
        except Exception as e:
            self.lawText.append(f'Произошла ошибка при поиске закона: {e}')

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LegalGuide()
    window.show()
    sys.exit(app.exec())