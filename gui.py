from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextBrowser, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from qfluentwidgets import TogglePushButton, DropDownPushButton, RoundMenu, Action, PrimaryPushButton
from search import search_law

class LegalGuide(QMainWindow):
    def __init__(self):
        super().__init__()

        # Инициализация переменных
        self.law_type = ''
        self.law_type_buttons = []
        self.law_type_map = {
            'УК': ('uk', 'УГОЛОВНЫЙ КОДЕКС'),
            'ТК': ('tk', 'ТРУДОВОЙ КОДЕКС'),
            'ГК': ('gk', 'ГРАЖДАНСКИЙ КОДЕКС'),
            'КОАП': ('koap', 'КОДЕКС ОБ АДМИНИСТРАТИВНЫХ ПРАВОНАРУШЕНИЯХ'),
            'Конституция': ('konstitucia', 'КОНСТИТУЦИЯ'),
            'ЗК': ('zk', 'ЗЕМЕЛЬНЫЙ КОДЕКС')
        }

        # Инициализация пользовательского интерфейса
        self.initUI()

    def initUI(self):
        # Установка заголовка окна
        self.setWindowTitle("Правовой справочник")

        # Установка шрифта
        self.setFont(QFont('Segoe UI', 12))

        # Установка размеров окна
        self.setGeometry(100, 100, 800, 600)

        # Установка иконки приложения
        self.setWindowIcon(QIcon('icon.png'))

        # Создание центрального виджета и главного макета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Панель выбора типа закона
        law_type_panel = QWidget()
        law_type_layout = QVBoxLayout(law_type_panel)
        main_layout.addWidget(law_type_panel)

        law_type_label = QLabel("Выберите вид закона")
        law_type_layout.addWidget(law_type_label)

        # Добавление кнопок выбора типа закона
        self.add_law_type_button(law_type_layout, "УК")
        self.add_law_type_button(law_type_layout, "ТК")
        self.add_law_type_button(law_type_layout, "ГК")
        self.add_law_type_button(law_type_layout, "КОАП")
        self.add_law_type_button(law_type_layout, "Конституция")

        # Кнопка для дополнительных типов законов
        more_laws_button = DropDownPushButton('...')
        more_laws_menu = RoundMenu(parent=more_laws_button)
        more_laws_menu.addAction(Action('ЗК', triggered=lambda: self.law_type_selected("ЗК", None)))
        more_laws_button.setMenu(more_laws_menu)
        law_type_layout.addWidget(more_laws_button)

        law_type_layout.addStretch(1)

        # Панель поиска
        search_panel = QWidget()
        search_layout = QVBoxLayout(search_panel)
        search_panel.setFixedWidth(200)
        main_layout.addWidget(search_panel)

        search_label = QLabel("Введите номер закона")
        search_layout.addWidget(search_label)

        self.law_number_entry = QLineEdit()
        search_layout.addWidget(self.law_number_entry)

        search_button = PrimaryPushButton('Поиск')
        search_button.clicked.connect(self.search_law)
        search_layout.addWidget(search_button)

        self.law_text = QTextBrowser()
        main_layout.addWidget(self.law_text)

        # Пространство для выравнивания QTextBrowser вверху
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        search_layout.addSpacerItem(spacer)

    # Добавление кнопки выбора типа закона
    def add_law_type_button(self, layout, button_text):
        button = TogglePushButton(button_text)
        button.clicked.connect(lambda: self.law_type_selected(button_text, button))
        layout.addWidget(button)
        self.law_type_buttons.append(button)

    # Обработчик выбора типа закона
    def law_type_selected(self, law_type, selected_button):
        self.law_type, full_law_name = self.law_type_map[law_type]
        for button in self.law_type_buttons:
            if button is not selected_button:
                button.setChecked(False)
        self.law_text.clear()
        self.law_text.append(f"Выбран тип закона: {full_law_name}")

    # Обработчик нажатия кнопки поиска
    def search_law(self):
        law_number = self.law_number_entry.text()
        search_law(self.law_type, law_number, self.law_text)