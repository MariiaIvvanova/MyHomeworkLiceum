from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QCheckBox, QDialog, QLineEdit, \
    QFormLayout, QDialogButtonBox
from PyQt5 import uic

from datetime import datetime, timedelta


DAYS_WEEK = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}
MONTHS = {
    "January": "Январь",
    "February": "Февраль",
    "March": "Март",
    "April": "Апрель",
    "May": "Май",
    "June": "Июнь",
    "July": "Июль",
    "August": "Август",
    "September": "Сентябрь",
    "October": "Октябрь",
    "November": "Ноябрь",
    "December": "Декабрь"
}


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        uic.loadUi('MyHomework.ui', self)
        self.setWindowTitle("MyHomework")

        self.connect_push()

        self.show_schedule_homework(self.current_date)  # Отображаем расписание на текущий день

    def connect_push(self):
        self.choose_file.triggered.connect(self.controller.import_schedule)

        self.addles_push.clicked.connect(self.open_add_lesson_dialog)
        self.delles_push.clicked.connect(self.open_del_lesson_dialog)
        self.addhom_push.clicked.connect(self.open_add_homework_dialog)
        self.delhom_push.clicked.connect(self.open_del_homework_dialog)

        self.current_date = datetime.now().strftime('%Y-%m-%d')

        self.nextday_push.clicked.connect(lambda: self.change_date("next"))     # Подключаем кнопки
        self.prevday_push.clicked.connect(lambda: self.change_date("prev"))

    def change_date(self, status):
        current_date_obj = datetime.strptime(self.current_date, '%Y-%m-%d')

        if status == "prev":
            new_date = current_date_obj - timedelta(days=1)
        elif status == "next":
            new_date = current_date_obj + timedelta(days=1)
        else:
            print(f"Некорректный статус: {status}")
            return

        self.current_date = new_date.strftime('%Y-%m-%d')
        self.show_schedule_homework(self.current_date)

    def show_schedule_homework(self, current_date):
        self.update_date_on_label()
        self.setup_table()

        lessons = self.controller.load_schedule_for_day(current_date)
        homework = self.controller.get_homework_for_day(current_date)
        # Проверяем, есть ли данные, чтобы отобразить
        if not lessons and not homework:
            self.homeworkTable.setColumnCount(1)
            self.homeworkTable.setHorizontalHeaderLabels([":-)"])
            self.homeworkTable.horizontalHeader().setStretchLastSection(True)
            self.homeworkTable.setRowCount(2)
            self.homeworkTable.setItem(0, 0, QTableWidgetItem("Уроков и мероприятий на сегодня нет"))
            self.homeworkTable.setItem(0, 1, QTableWidgetItem("Уроков и мероприятий на этот день не найдено"))
            return

        # Отображаем расписание и домашку
        self.display_schedule_homework(lessons, homework)

    def display_schedule_homework(self, lessons, homework):
        self.homeworkTable.setRowCount(0)

        homework_dict = {hw[0]: hw[1:] for hw in homework}  # {название урока: [домашка, дедлайн, статус, id]}

        for row_count, lesson in enumerate(lessons):
            self.homeworkTable.insertRow(row_count)
            self.homeworkTable.setItem(row_count, 0, QTableWidgetItem(str(lesson[2])))  # id
            self.homeworkTable.setItem(row_count, 1, QTableWidgetItem(lesson[1]))  # Время
            self.homeworkTable.setItem(row_count, 2, QTableWidgetItem(lesson[0]))   # Урок

            # есть ли домашка для данного урока
            if lesson[0] in homework_dict:
                hw = homework_dict[lesson[0]]
                self.homeworkTable.setItem(row_count, 3, QTableWidgetItem(hw[0]))  # Домашка
                self.homeworkTable.setItem(row_count, 4, QTableWidgetItem(hw[1]))  # Дедлайн
                checkbox = QCheckBox("Выполнено")
                checkbox.setChecked(hw[2] == 1)  # Устанавливаем статус выполнения
                checkbox.stateChanged.connect(lambda state, hw_id=hw[3]: self.controller.update_status_homework(hw_id, state))
                self.homeworkTable.setCellWidget(row_count, 5, checkbox)

            else:
                # пустыe ячейки
                self.homeworkTable.setItem(row_count, 3, QTableWidgetItem(''))
                self.homeworkTable.setItem(row_count, 4, QTableWidgetItem(''))
                self.homeworkTable.setItem(row_count, 5, QTableWidgetItem(''))

    def update_date_on_label(self):
        # Преобразуем строку даты в объект datetime
        current_date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
        day_of_week = current_date_obj.weekday()  # Получаем число от 0 до 6

        month_english = current_date_obj.strftime("%B")
        month_russian = MONTHS.get(month_english, month_english)
        # Форматируем строку на русский
        formatted_date = current_date_obj.strftime(f"%d {month_russian}")

        self.label.setText(f"{DAYS_WEEK[day_of_week]}, {formatted_date}")
        self.label.adjustSize()

    def setup_table(self):
        self.homeworkTable.setColumnCount(6)
        self.homeworkTable.setHorizontalHeaderLabels(["id", "Время", "Урок", "Домашка", "Дедлайн", "Статус"])

        self.homeworkTable.setColumnWidth(0, 35)
        self.homeworkTable.setColumnWidth(1, 50)
        self.homeworkTable.setColumnWidth(2, 85)
        self.homeworkTable.setColumnWidth(3, 230)
        self.homeworkTable.setColumnWidth(4, 85)
        self.homeworkTable.setColumnWidth(5, 100)

    def show_message(self, message):
        # Отображает ошибку в статус-баре.
        self.statusBar().clearMessage()
        self.statusBar().setStyleSheet("color: red;")
        self.statusBar().showMessage(f"Ошибка: {message}")

    def open_add_lesson_dialog(self):
        # Создаем диалоговое окно
        dialog = AddLessonDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            lesson_name, time = dialog.get_input_data()
            self.controller.add_lesson(self.current_date, lesson_name, time)

    def open_del_lesson_dialog(self):
        dialog = DeleteLessonDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            lesson_id = dialog.get_input_data()
            self.controller.del_lesson(lesson_id)

    def open_add_homework_dialog(self):
        dialog = AddHomeworkDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            lesson_id = dialog.get_input_data()
            self.controller.add_homework(lesson_id)

    def open_del_homework_dialog(self):
        dialog = DeleteHomeworkDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            lesson_id = dialog.get_input_data()
            self.controller.delete_homework(lesson_id)


class AddLessonDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить урок")

        # Создаем поля для ввода данных
        self.lesson_name_input = QLineEdit(self)
        self.lesson_time_input = QLineEdit(self)

        # Формируем форму для ввода данных
        form_layout = QFormLayout(self)
        form_layout.addRow("Название урока:", self.lesson_name_input)
        form_layout.addRow("Время урока:", self.lesson_time_input)

        # Кнопки для подтверждения
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        form_layout.addWidget(button_box)

        self.setLayout(form_layout)

    def get_input_data(self):
        # Получаем данные из полей ввода
        lesson_name = self.lesson_name_input.text()
        time = self.lesson_time_input.text()
        return (lesson_name, time)


class DeleteLessonDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удалить урок")

        # Создаем поля для ввода данных
        self.lesson_id = QLineEdit(self)

        # Формируем форму для ввода данных
        form_layout = QFormLayout(self)
        form_layout.addRow("Айди урока:", self.lesson_id)

        # Кнопки для подтверждения
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        form_layout.addWidget(button_box)

        self.setLayout(form_layout)

    def get_input_data(self):
        # Получаем данные из полей ввода
        lesson_id = self.lesson_id.text()
        return lesson_id


class AddHomeworkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить домашнее задание")

        # Создаем поля для ввода данных
        self.lesson_id = QLineEdit(self)
        self.description = QLineEdit(self)
        self.deadline = QLineEdit(self)

        # Формируем форму для ввода данных
        form_layout = QFormLayout(self)
        form_layout.addRow("Айди урока:", self.lesson_id)
        form_layout.addRow("Задание урока:", self.description)
        form_layout.addRow("Дедлайн:", self.deadline)

        # Кнопки для подтверждения
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        form_layout.addWidget(button_box)

        self.setLayout(form_layout)

    def get_input_data(self):
        # Получаем данные из полей ввода
        lesson_id = self.lesson_id.text()
        description = self.description.text()
        deadline = self.deadline.text()
        return [lesson_id, description, deadline]


class DeleteHomeworkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удалить домашнее задание")

        # Создаем поля для ввода данных
        self.lesson_id = QLineEdit(self)

        # Формируем форму для ввода данных
        form_layout = QFormLayout(self)
        form_layout.addRow("Айди урока:", self.lesson_id)

        # Кнопки для подтверждения
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        form_layout.addWidget(button_box)

        self.setLayout(form_layout)

    def get_input_data(self):
        # Получаем данные из полей ввода
        lesson_id = self.lesson_id.text()
        return lesson_id
