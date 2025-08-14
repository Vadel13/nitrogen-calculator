import sys
from PyQt6.QtWidgets import QApplication
from ui import CalculatorUI

# Главная функция запуска
def main():
    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Создаем и настраиваем главное окно
    window = CalculatorUI()
    window.show()  # Показываем окно
    
    # Запускаем приложение
    sys.exit(app.exec())

# Запускаем только если это главный файл
if __name__ == "__main__":
    main()