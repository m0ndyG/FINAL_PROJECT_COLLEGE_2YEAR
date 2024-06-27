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

# Загрузка данных для токенизации предложений.
nltk.download('punkt')

# Базовый URL-адрес сайта с правовой информацией.
BASE_URL = 'https://www.zakonrf.info'
# Заголовки для HTTP-запросов.
headers = {'user-agent': 'Mozilla/5.0'}  
# Создание сессии для отправки HTTP-запросов.
session = requests.Session()  

class LegalGuide(QMainWindow):
    def __init__(self):
        super().__init__()

        # Словарь для хранения кодов и полных названий законов.
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

        # Выбранный код закона (например, 'uk', 'gk').
        self.selected_law_code = ''  
        # Список кнопок выбора типа закона.
        self.law_code_buttons = []  
        # Список истории поиска.
        self.search_history = []  

        # Инициализация пользовательского интерфейса.
        self.initUI()

    def initUI(self):
        # Установка параметров окна.
        self.setWindowTitle("Правовой справочник")
        self.setFont(QFont('Segoe UI', 12))
        self.setGeometry(100, 100, 800, 600)
        # Установка иконки для окна.
        self.setWindowIcon(QIcon('icon.png'))  

        # Основной виджет и его разметка.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Панели для выбора типа закона и поиска.
        self.create_law_code_panel(main_layout) 
        self.create_search_panel(main_layout)  

        # Текстовый браузер для отображения результатов.
        self.law_text = QTextBrowser()
        main_layout.addWidget(self.law_text)

    
    def create_law_code_panel(self, main_layout):
        # Виджет панели и его вертикальная разметка.
        law_type_panel = QWidget()  
        law_type_layout = QVBoxLayout(law_type_panel)  
        # Фиксированная ширина панели.
        law_type_panel.setFixedWidth(200) 
        # Добавление панели в основную разметку.
        main_layout.addWidget(law_type_panel)

        # Надпись "Выберите вид закона".
        law_type_label = QLabel("Выберите вид закона")
        law_type_layout.addWidget(law_type_label)

        # Кнопки для основных типов законов.
        for law_code in ["УК", "ТК", "ГК", "КОАП", "Конституция"]:
            self.add_law_code_button(law_type_layout, law_code)

        # Кнопка "Еще" с выпадающим меню для остальных законов.
        more_laws_button = DropDownPushButton('...')
        more_laws_button.setFixedWidth(150)
        # Меню для кнопки "Еще".
        more_laws_menu = RoundMenu(parent=more_laws_button)

        # Пункты меню для каждого закона из словаря.
        more_laws_menu.addAction(Action('ЗК', triggered=lambda: self.law_code_selected("ЗК", more_laws_button)))
        more_laws_menu.addAction(Action('ЖК', triggered=lambda: self.law_code_selected("ЖК", more_laws_button)))
        more_laws_menu.addAction(Action('УПК', triggered=lambda: self.law_code_selected("УПК", more_laws_button)))
        
        # Установка меню для кнопки "Еще".
        more_laws_button.setMenu(more_laws_menu) 
        # Добавление кнопки на панель.
        law_type_layout.addWidget(more_laws_button)

        # Растягивающий элемент для отступа снизу.
        law_type_layout.addStretch(1)

        # Надпись "История поиска".
        history_label = QLabel("История поиска")
        law_type_layout.addWidget(history_label)

        # Список истории поиска.
        self.history_list = QListWidget()
        # Политика размеров для списка.
        self.history_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Подключение обработчика клика по элементу списка.
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        # Добавление списка на панель.
        law_type_layout.addWidget(self.history_list) 

    
    def create_search_panel(self, main_layout):
        # Виджет панели и его вертикальная разметка.
        search_panel = QWidget()
        search_layout = QVBoxLayout(search_panel)
        # Фиксированная ширина панели.
        search_panel.setFixedWidth(200)
        # Добавление панели в основную разметку.
        main_layout.addWidget(search_panel)

        # Надпись "Введите номер закона".
        search_label = QLabel("Введите номер закона")
        search_layout.addWidget(search_label)

        # Поле ввода для номера закона.
        self.law_number_entry = QLineEdit()
        search_layout.addWidget(self.law_number_entry)

        # Кнопка "Поиск".
        search_button = PrimaryPushButton('Поиск')
        search_button.setFixedWidth(150)
        # Подключение обработчика поиска по клику на кнопку.
        search_button.clicked.connect(self.search_law) 
        search_layout.addWidget(search_button)

        # Растягивающий элемент для отступа.
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        search_layout.addSpacerItem(spacer)

    # Метод для добавления кнопки выбора типа закона на панель.
    def add_law_code_button(self, layout, button_text):
        # Кнопка с текстом.
        button = TogglePushButton(button_text)  
        # Фиксированная ширина кнопки.
        button.setFixedWidth(150)
        # Подключение обработчика выбора закона по клику.
        button.clicked.connect(lambda: self.law_code_selected(button_text, button))
        # Добавление кнопки на панель.
        layout.addWidget(button)  
        # Добавление кнопки в список.
        self.law_code_buttons.append(button) 

    # Обработчик выбора типа закона.
    def law_code_selected(self, law_code, selected_button):
        # Получение кода для URL и полного названия закона из словаря.
        self.selected_law_code, full_law_name = self.law_codes[law_code]
        
        # Сброс выделения у всех кнопок, кроме выбранной.
        for button in self.law_code_buttons:
            if button is not selected_button:
                button.setChecked(False)

        # Очистка текстового браузера.
        self.law_text.clear()
        # Вывод выбранного типа закона.
        self.law_text.append(f"Выбран тип закона: {full_law_name}")

    # Метод поиска закона.
    def search_law(self):
        # Получение номера закона из поля ввода.
        law_number = self.law_number_entry.text()  

        # Проверка, выбран ли тип закона.
        if self.selected_law_code:
            # Получение полного названия закона по выбранному коду.
            law_full_name = next(full_name for short, full_name in self.law_codes.values() if short == self.selected_law_code)
            # Запуск поиска закона по коду и номеру.
            self.search_law_by_code(law_number, law_full_name)
        else:
            # Вывод сообщения об ошибке, если тип закона не выбран.
            self.law_text.append('Пожалуйста, выберите тип закона.')

    # Метод поиска закона по коду и номеру.
    def search_law_by_code(self, law_number, law_full_name):
        # Проверка корректности введенного номера закона.
        if not law_number.replace('.', '').isdigit():
            self.law_text.append('Пожалуйста, введите корректный номер закона.')
            return

        try:
            # Очистка текстового браузера.
            self.law_text.clear()
            # Формирование URL-адреса.
            url = f'{BASE_URL}/{self.selected_law_code}/{law_number}'
            # Отправка GET-запроса.
            response = session.get(url, headers=headers)  

            # Обработка ответа сервера.
            if response.status_code == 200:
                # Парсинг HTML-страницы.
                soup = BeautifulSoup(response.content, 'html.parser') 
                
                # Поиск элементов с названием и текстом закона.
                law_title_element = soup.find(class_='law-h1')  
                law_text_element = soup.find(class_='st-body content-body')

                # Извлечение текста из найденных элементов.
                law_title = law_title_element.text if law_title_element else 'Название закона не найдено.'
                law_text = law_text_element.text if law_text_element else 'Текст закона не найден.'

                # Разделение названия закона на предложения.
                sentences = sent_tokenize(law_title)
                first_sentence = sentences[0] if sentences else ''
                other_sentences = '\n'.join(sentences[1:]) if sentences else ''

                # Вывод найденной информации в текстовый браузер.
                self.law_text.append(
                    f'<b style="font-size: 14pt;">{first_sentence}</b><br>\n\n'
                    f'<b style="font-size: 14pt;">{other_sentences}</b><br>\n\n<br>\n'
                    f'{law_text}'
                )
                # Обновление истории поиска.
                self.update_search_history(law_number, law_full_name)
            else:
                # Вывод сообщения об ошибке, если закон не найден.
                self.law_text.append('Закон не найден или ошибка сервера.')
        except Exception as e:
            # Вывод сообщения об ошибке.
            self.law_text.append(f'Произошла ошибка при поиске закона: {e}')

    # Метод обновления истории поиска.
    def update_search_history(self, law_number, law_full_name):
        # Формирование записи истории.
        history_entry = f"{law_number} {law_full_name}" 
        # Проверка, есть ли уже такая запись в истории.
        if history_entry not in self.search_history:
            # Добавление записи в историю.
            self.search_history.append(history_entry) 
            # Добавление записи в список истории.
            self.history_list.addItem(history_entry)  

    # Обработчик клика по элементу истории поиска.
    def on_history_item_clicked(self, item):
        # Получение текста записи из списка.
        history_entry = item.text()  
        # Разделение записи на номер и название закона.
        law_number, law_full_name = history_entry.split(' ', 1)

        # Поиск кода закона по полному названию.
        for law_code, (short_name, full_name) in self.law_codes.items():
            if full_name == law_full_name:
                # Установка выбранного кода закона.
                self.selected_law_code = short_name 
                # Вставка номера закона в поле ввода.
                self.law_number_entry.setText(law_number)
                # Выбор типа закона.
                self.law_code_selected(law_code, None) 
                # Поиск закона.
                self.search_law_by_code(law_number, law_full_name) 
                break

# Точка входа в приложение.
if __name__ == '__main__':
    # Настройка высокого разрешения для экранов с высокой плотностью пикселей.
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough) 
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)                                             
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)     
    
    # Создание объекта приложения Qt.
    app = QApplication([])  
    # Создание объекта главного окна.
    window = LegalGuide()
    # Отображение окна.
    window.show()  
    # Запуск цикла обработки событий Qt.
    app.exec_()