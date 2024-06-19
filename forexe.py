import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextBrowser, QSpacerItem, QSizePolicy, QListWidget
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from qfluentwidgets import TogglePushButton, DropDownPushButton, RoundMenu, Action, PrimaryPushButton

nltk.download('punkt')

BASE_URL = 'https://www.zakonrf.info'
headers = {'user-agent': 'Mozilla/5.0'}
session = requests.Session()

class LegalGuide(QMainWindow):
    def __init__(self):
        super().__init__()

        # Словарь с кодами и полными названиями законов
        self.law_codes = {
            'УК': ('uk', 'УГОЛОВНЫЙ КОДЕКС'),
            'ТК': ('tk', 'ТРУДОВОЙ КОДЕКС'),
            'ГК': ('gk', 'ГРАЖДАНСКИЙ КОДЕКС'),
            'КОАП': ('koap', 'КОДЕКС ОБ АДМИНИСТРАТИВНЫХ ПРАВОНАРУШЕНИЯХ'),
            'Конституция': ('konstitucia', 'КОНСТИТУЦИЯ'),
            'ЗК': ('zk', 'ЗЕМЕЛЬНЫЙ КОДЕКС'),
            'ЖК': ('jk', 'ЖИЛИЩНЫЙ КОДЕКС'),
            'УПК': ('upk', 'УГОЛОВНО-ПРОЦЕССУАЛЬНЫЙ КОДЕКС')
        }

        # Инициализация атрибутов
        self.selected_law_code = ''
        self.law_code_buttons = []
        self.search_history = []

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Правовой справочник")
        self.setFont(QFont('Segoe UI', 12))
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('icon.png'))

        # Основные элементы интерфейса
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Панель выбора типа закона
        self.create_law_code_panel(main_layout)

        # Панель поиска
        self.create_search_panel(main_layout)

        # Текстовый браузер для отображения результатов поиска
        self.law_text = QTextBrowser()
        main_layout.addWidget(self.law_text)

    # Создание панели выбора типа закона
    def create_law_code_panel(self, main_layout):
        law_type_panel = QWidget()
        law_type_layout = QVBoxLayout(law_type_panel)
        law_type_panel.setFixedWidth(200)
        main_layout.addWidget(law_type_panel)

        law_type_label = QLabel("Выберите вид закона")
        law_type_layout.addWidget(law_type_label)

        # Кнопки для основных типов законов
        for law_code in ["УК", "ТК", "ГК", "КОАП", "Конституция"]:
            self.add_law_code_button(law_type_layout, law_code)

        # Кнопка "Еще" для раскрывающегося меню
        more_laws_button = DropDownPushButton('...')
        more_laws_button.setFixedWidth(150)
        more_laws_menu = RoundMenu(parent=more_laws_button)
        more_laws_menu.addAction(Action('ЗК', triggered=lambda: self.law_code_selected("ЗК", more_laws_button)))
        more_laws_menu.addAction(Action('ЖК', triggered=lambda: self.law_code_selected("ЖК", more_laws_button)))
        more_laws_menu.addAction(Action('УПК', triggered=lambda: self.law_code_selected("УПК", more_laws_button)))
        more_laws_button.setMenu(more_laws_menu)
        law_type_layout.addWidget(more_laws_button)

        law_type_layout.addStretch(1)

        # Заголовок истории поиска
        history_label = QLabel("История поиска")
        law_type_layout.addWidget(history_label)

        # Список истории поиска
        self.history_list = QListWidget()
        self.history_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        law_type_layout.addWidget(self.history_list)

    # Создание панели поиска
    def create_search_panel(self, main_layout):
        search_panel = QWidget()
        search_layout = QVBoxLayout(search_panel)
        search_panel.setFixedWidth(200)
        main_layout.addWidget(search_panel)

        # Заголовок панели поиска
        search_label = QLabel("Введите номер закона")
        search_layout.addWidget(search_label)

        # Поле ввода номера закона
        self.law_number_entry = QLineEdit()
        search_layout.addWidget(self.law_number_entry)

        # Кнопка поиска
        search_button = PrimaryPushButton('Поиск')
        search_button.setFixedWidth(150)
        search_button.clicked.connect(self.search_law)
        search_layout.addWidget(search_button)

        # Растягивающий элемент на панели поиска
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        search_layout.addSpacerItem(spacer)

    # Добавить кнопку для выбора типа закона
    def add_law_code_button(self, layout, button_text):
        button = TogglePushButton(button_text)
        button.setFixedWidth(150)
        button.clicked.connect(lambda: self.law_code_selected(button_text, button))
        layout.addWidget(button)
        self.law_code_buttons.append(button)

    # Обработчик выбора типа закона
    def law_code_selected(self, law_code, selected_button):
        self.selected_law_code, full_law_name = self.law_codes[law_code]
        # Сбросить выделение у всех кнопок, кроме выбранной
        for button in self.law_code_buttons:
            if button is not selected_button:
                button.setChecked(False)
        self.law_text.clear()
        self.law_text.append(f"Выбран тип закона: {full_law_name}")

    # Поиск закона
    def search_law(self):
        law_number = self.law_number_entry.text()
        if self.selected_law_code:
            law_full_name = next(full_name for short, full_name in self.law_codes.values() if short == self.selected_law_code)
            self.search_law_by_code(law_number, law_full_name)
        else:
            self.law_text.append('Пожалуйста, выберите тип закона.')

    def search_law_by_code(self, law_number, law_full_name):
        if not law_number.replace('.', '').isdigit():
            self.law_text.append('Пожалуйста, введите корректный номер закона.')
            return

        try:
            self.law_text.clear()
            url = f'{BASE_URL}/{self.selected_law_code}/{law_number}'
            response = session.get(url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                law_title_element = soup.find(class_='law-h1')
                law_text_element = soup.find(class_='st-body content-body')

                law_title = law_title_element.text if law_title_element else 'Название закона не найдено.'
                law_text = law_text_element.text if law_text_element else 'Текст закона не найден.'

                sentences = sent_tokenize(law_title)
                first_sentence = sentences[0] if sentences else ''
                other_sentences = '\n'.join(sentences[1:]) if sentences else ''

                self.law_text.append(f'<b style="font-size: 14pt;">{first_sentence}</b><br>\n\n<b style="font-size: 14pt;">{other_sentences}</b><br>\n\n<br>\n{law_text}')
                self.update_search_history(law_number, law_full_name)
            else:
                self.law_text.append('Закон не найден или ошибка сервера.')
        except requests.exceptions.RequestException:
            self.law_text.append('Ошибка: Проверьте подключение к интернету.')
        except Exception as e:
            self.law_text.append(f'Произошла ошибка при поиске закона: {e}')

    # Обновить историю поиска
    def update_search_history(self, law_number, law_full_name):
        history_entry = f"{law_number} {law_full_name}"
        if history_entry not in self.search_history:
            self.search_history.append(history_entry)
            self.history_list.addItem(history_entry)

    # Обработчик клика по элементу истории поиска
    def on_history_item_clicked(self, item):
        history_entry = item.text()
        law_number, law_full_name = history_entry.split(' ', 1)
        for law_code, (short_name, full_name) in self.law_codes.items():
            if full_name == law_full_name:
                self.selected_law_code = short_name
                self.law_number_entry.setText(law_number)
                self.law_code_selected(law_code, None)
                self.search_law_by_code(law_number, law_full_name)
                break


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)     
    app = QApplication([])
    window = LegalGuide()
    window.show()
    app.exec_()
