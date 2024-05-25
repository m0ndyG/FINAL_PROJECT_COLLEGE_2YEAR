import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import nltk
from nltk.tokenize import sent_tokenize

# Загрузка модуля для разбиения текста на предложения
nltk.download('punkt')

# Базовый URL для законов
BASE_URL = 'https://www.zakonrf.info'

# Заголовки для имитации браузерного запроса
headers = {'user-agent': UserAgent().random}

# Создание сессии для отправки HTTP-запросов
session = requests.Session()

def search_law(law_type, law_number, text_browser):
    # Проверка корректности введенного номера закона
    if not law_number.isdigit():
        text_browser.append('Пожалуйста, введите корректный номер закона.')
        return

    try:
        # Очистка текстового браузера
        text_browser.clear()

        # Формирование URL для запроса
        url = f'{BASE_URL}/{law_type}/{law_number}'

        # Отправка HTTP-запроса
        response = session.get(url, headers=headers)

        if response.status_code == 200:
            # Парсинг HTML-страницы
            soup = BeautifulSoup(response.content, 'html.parser')
            law_title_element = soup.find(class_='law-h1')
            law_text_element = soup.find(class_='st-body content-body')

            # Извлечение названия и текста закона из HTML
            law_title = law_title_element.text if law_title_element else 'Название закона не найдено.'
            law_text = law_text_element.text if law_text_element else 'Текст закона не найден.'

            # Разбиение названия закона на предложения
            sentences = sent_tokenize(law_title)
            first_sentence = sentences[0] if sentences else ''
            other_sentences = '\n'.join(sentences[1:]) if sentences else ''

            # Отображение названия и текста закона в текстовом браузере
            text_browser.append(f'<b style="font-size: 14pt;">{first_sentence}</b><br>\n\n<b style="font-size: 14pt;">{other_sentences}</b><br>\n\n<br>\n{law_text}')
        else:
            text_browser.append('Закон не найден или ошибка сервера.')
    except Exception as e:
        text_browser.append(f'Произошла ошибка при поиске закона: {e}')