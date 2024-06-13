import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

BASE_URL = 'https://www.zakonrf.info'
headers = {'user-agent': UserAgent().random}
session = requests.Session()

def search_law(law_code, law_number, text_browser):
    if not law_number.replace('.', '').isdigit():
        text_browser.append('Пожалуйста, введите корректный номер закона.')
        return False

    try:
        text_browser.clear()
        url = f'{BASE_URL}/{law_code}/{law_number}'
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

            text_browser.append(f'<b style="font-size: 14pt;">{first_sentence}</b><br>\n\n<b style="font-size: 14pt;">{other_sentences}</b><br>\n\n<br>\n{law_text}')
            return True
        else:
            text_browser.append('Закон не найден или ошибка сервера.')
            return False
    except Exception as e:
        text_browser.append(f'Произошла ошибка при поиске закона: {e}')
        return False
