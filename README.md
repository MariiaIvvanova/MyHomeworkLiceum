
# MyHomework

**MyHomework** — это приложение для управления домашними заданиями и школьным расписанием. Оно помогает школьникам организовать свое время, добавлять задания и отслеживать их выполнение.

## Основные функции
- Редактирование школьного расписания.
- Добавление домашнего задания.
- Отметка выполненных заданий.
- Сохранение данных в локальной базе данных для доступа после перезапуска приложения.

## Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/MariiaIvvanova/MyHomeworkLiceum.git
   cd MyHomework
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Использование
1. Запустите приложение:
   ```bash
   python main.py
   ```
2. Следуйте интерфейсу для управления расписанием и заданиями.

## Структура проекта
- **main.py**: Точка входа в приложение.
- **db_manger.py**: Работа с базой данных.
- **view.py**: Логика пользовательского интерфейса.
- **MyHomework.ui**: Файл дизайна интерфейса (создан в Qt Designer).
- **requirements.txt**: Список необходимых зависимостей.
- **README.md**: Документация проекта.

## Требования
- Python 3.9+
- PyQt5
- SQLite (встроенный в Python)
