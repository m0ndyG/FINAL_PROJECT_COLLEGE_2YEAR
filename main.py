import sys
from PyQt5.QtWidgets import QApplication
from gui import LegalGuide

if __name__ == '__main__':
    # Создание экземпляра приложения Qt
    app = QApplication(sys.argv)

    # Создание экземпляра главного окна
    window = LegalGuide()

    # Отображение главного окна
    window.show()

    # Запуск цикла событий приложения
    sys.exit(app.exec_())