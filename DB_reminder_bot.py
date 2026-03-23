import sqlite3
import os

class Database:
    def init(self, db_name="reminders.db"):
        """Инициализация базы данных"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.create_tables()
    
    def connect(self):
        """Создание соединения с базой данных"""
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Создание необходимых таблиц"""
        self.connect()
        
        # Таблица для заметок
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_user INTEGER NOT NULL,
                note_text TEXT NOT NULL,
                date INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        self.close()
    
    def write(self, data):
        """Запись заметки в базу данных
        data: [user_id, note_text, timestamp]
        """
        try:
            self.connect()
            self.cursor.execute('''
                INSERT INTO notes (id_user, note_text, date)
                VALUES (?, ?, ?)
            ''', (data[0], data[1], data[2]))
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"Ошибка при записи в БД: {e}")
            return False
    
    def read(self, field, value):
        """Чтение заметок по полю"""
        try:
            self.connect()
            self.cursor.execute(f'''
                SELECT * FROM notes WHERE {field} = ? ORDER BY date
            ''', (value,))
            result = self.cursor.fetchall()
            self.close()
            
            # Всегда возвращаем список, даже если одна запись
            return result if result else []
        except Exception as e:
            print(f"Ошибка при чтении из БД: {e}")
            return []
    
    def read_all(self):
        """Чтение всех заметок"""
        try:
            self.connect()
            self.cursor.execute('SELECT * FROM notes ORDER BY date')
            result = self.cursor.fetchall()
            self.close()
            return result
        except Exception as e:
            print(f"Ошибка при чтении всех заметок: {e}")
            return []
    
    def delete_row(self, field, value):
        """Удаление заметки по полю"""
        try:
            self.connect()
            self.cursor.execute(f'''
                DELETE FROM notes WHERE {field} = ?
            ''', (value,))
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"Ошибка при удалении из БД: {e}")
            return False
    
    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        """Добавление пользователя в базу данных"""
        try:
            self.connect()
            self.cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении пользователя: {e}")
            return False
    
    def get_user_notes_count(self, user_id):
        """Получение количества заметок пользователя"""
      try:
            self.connect()
            self.cursor.execute('''
                SELECT COUNT(*) FROM notes WHERE id_user = ?
            ''', (user_id,))
            count = self.cursor.fetchone()[0]
            self.close()
            return count
        except Exception as e:
            print(f"Ошибка при подсчете заметок: {e}")
            return 0

# Создаем экземпляры для использования в основном файле
notes = Database()
users = Database()
