import sys

from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog

from db_manger import DatabaseManager
from view import MainWindow


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def load_schedule_for_day(self, date):
        # загружаем расписание
        lessons = self.model.get_schedule_for_day(date)
        return lessons

    def get_homework_for_day(self, date):
        # Получаем домашку для указанного дня
        return self.model.get_homework_for_day(date)

    def update_status_homework(self, hw_id, state):
        status = 1 if state == 2 else 0  # Преобразуем чекбокс
        self.model.update_is_completed(hw_id, status)

    def import_schedule(self):
        self.show_instructions()
        # Открываем диалог для выбора файла
        file_name, _ = QFileDialog.getOpenFileName(
            self.view,
            "Выберите файл",
            "",
            "CSV файлы (*.csv)"
        )
        if file_name:
            try:
                self.model.import_schedule_from_file(file_name)

                self.show_message("Успех", "Расписание успешно загружено.")
            except ValueError as e:
                self.show_message("Ошибка", f"Не удалось загрузить расписание: {str(e)}")
            except Exception as e:
                self.show_message("Ошибка", f"Произошла ошибка: {str(e)}")

    def show_message(self, title, message):
        # Показываем диалоговое окно с сообщением
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information if title == "Успех" else QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def show_instructions(self):
        # окно с инструкцией
        QMessageBox.information(
            self.view,
            "Инструкция",
            "Пожалуйста, выберите .csv файл, содержащий колонки:\n\n- day\n- lesson_name\n- time\n- с разделителем ','\n"
            "Убедитесь, что файл соответствует этому формату."
        )

    def add_lesson(self, date, lesson_name, time):
        # Добавления урока
        if not lesson_name:
           message = "Поле с именем не должно быть пустым"
           self.view.show_message(message)
        else:
            if not time:
                time = "--"
            self.model.add_lesson((date, lesson_name, time))

    def del_lesson(self, lesson_id):
        # Удаления урока
        if lesson_id:
           self.model.delete_lesson(lesson_id)
        else:
            message = "Поле айди не должно быть пустым"
            self.view.show_message(message)

    def add_homework(self, lesson_data):
        # Добавления домашнего задания
        if lesson_data[0]:
            if not lesson_data[1]:
                lesson_data[1] = "нет задания"
            if not lesson_data[2]:
                lesson_data[2] = "--"
            self.model.add_homework(lesson_data)
        else:
            message = "Поле айди не должно быть пустым"
            self.view.show_message(message)

    def delete_homework(self, lesson_id):
        # Удаление домашнего задания
        if not lesson_id:
            message = "Поле айди не должно быть пустым"
            self.view.show_message(message)
        else:
            self.model.delete_homework(lesson_id)


def main():
    # главная функция
    app = QApplication(sys.argv)
    db_manager = DatabaseManager()
    controller = Controller(db_manager, None)
    main_window = MainWindow(controller)
    controller.view = main_window
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
