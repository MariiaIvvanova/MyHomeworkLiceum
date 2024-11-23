import csv
import sqlite3
from datetime import datetime, timedelta


class DatabaseManager:
    def __init__(self, db_name="schedule.db"):
        self.con = sqlite3.connect(db_name)
        self.cursor = self.con.cursor()
        self.create_tables()

    def create_tables(self):
        # Создание таблицы расписания
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            date TEXT NOT NULL, -- Дата в формате YYYY-MM-DD
            lesson_name TEXT NOT NULL,
            time TEXT NOT NULL
        )''')
        self.con.commit()

        # Создание таблицы домашних заданий
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS homework (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER NOT NULL,
            description TEXT DEFAULT '',
            deadline TEXT,
            is_completed INTEGER DEFAULT 0,
            FOREIGN KEY (lesson_id) REFERENCES schedule(id) ON DELETE CASCADE
        )''')
        self.con.commit()

    def close_connection(self):
        self.con.close()

    def get_schedule_for_day(self, date):
        # Получить расписание на указанием времени
        self.cursor.execute('''SELECT lesson_name, time, id FROM schedule
                               WHERE date = ?
                               ORDER BY time''', (date,))
        return self.cursor.fetchall()

    def get_homework_for_day(self, date):
        # Получить домашнее задание на день
        self.cursor.execute('''SELECT schedule.lesson_name, homework.description, homework.deadline, homework.is_completed, homework.id
        FROM homework
        JOIN schedule ON homework.lesson_id = schedule.id
        WHERE schedule.date = ?
        ORDER BY homework.deadline''', (date,))
        return self.cursor.fetchall()

    def add_lesson(self, lesson_data):
        # Добавить урок
        self.cursor.execute('''INSERT INTO schedule (date, lesson_name, time)
        VALUES(?, ?, ?)''', lesson_data)
        self.con.commit()

    def delete_lesson(self, id):
        # Удаление урока
        self.cursor.execute('''DELETE FROM schedule WHERE id = ?''', (id,))
        self.con.commit()

    def import_schedule_from_file(self, file_name, weeks_count=3):
        # Определяем дату понедельника текущей недели
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())  # понедельник текущей недели

        days_week = {
            "Понедельник": 0,
            "Вторник": 1,
            "Среда": 2,
            "Четверг": 3,
            "Пятница": 4,
            "Суббота": 5,
            "Воскресенье": 6
        }

        with open(file_name, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            if 'day' not in reader.fieldnames or 'lesson_name' not in reader.fieldnames or 'time' not in reader.fieldnames:
                raise ValueError("Файл имеет неверный формат. Ожидаются заголовки: day, lesson_name, time.")

            for week in range(weeks_count):
                # Для каждой недели вычисляем дату начала
                week_start_date = start_of_week + timedelta(weeks=week)
                csvfile.seek(0)
                next(reader)

                for row in reader:
                    day = row['day'].strip()
                    lesson_name = row['lesson_name'].strip()
                    time = row['time'].strip()

                    if day in days_week:
                        lesson_date = week_start_date + timedelta(days=days_week[day])
                        lesson_date_str = lesson_date.strftime('%Y-%m-%d')

                        self.add_lesson((lesson_date_str, lesson_name, time))
                    else:
                        print(f"Ошибка: День '{day}' не найден в словаре дней. Строка пропущена.")

            self.con.commit()

    def update_is_completed(self, id, status=1):
        self.cursor.execute('''UPDATE homework SET is_completed = ? WHERE id = ?''', (status, id))
        self.con.commit()
        return self.cursor.rowcount

    def delete_homework(self, lesson_id):
        # Удалить домашнее задание для указанного урока
        self.cursor.execute('''DELETE FROM homework WHERE lesson_id = ?''', (lesson_id,))
        self.con.commit()

    def add_homework(self, homework_data):
        # Проверяем, есть ли уже домашнее задание для данного урока
        lesson_id = homework_data[0]
        self.cursor.execute('''SELECT id FROM homework WHERE lesson_id = ?''', (lesson_id,))
        existing_homework = self.cursor.fetchone()

        if existing_homework:
            self.delete_homework(lesson_id)

        # Добавляем новое домашнее задание
        self.cursor.execute('''INSERT INTO homework (lesson_id, description, deadline)
        VALUES(?, ?, ?)''', homework_data)
        self.con.commit()
