import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),  # Адрес сервера MySQL из .env
            port=os.getenv("DB_PORT"),  # Порт из .env
            user=os.getenv("DB_USER"),  # Имя пользователя из .env
            password=os.getenv("DB_PASSWORD"),  # Пароль из .env
        )
        if conn.is_connected():
            print("Подключение к MySQL успешно!")
            return conn
    except Error as e:
        print(f"Ошибка подключения к MySQL: {e}")
        return None

def init_database():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Создание базы данных, если её ещё нет
            cursor.execute("CREATE DATABASE IF NOT EXISTS clothing_classification;")
            print("База данных 'clothing_logs' успешно создана или уже существует.")

            # Подключение к созданной базе данных
            conn.database = 'clothing_classification'

            # Создание таблицы logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45) NOT NULL,
                    method VARCHAR(10) NOT NULL,
                    path VARCHAR(255) NOT NULL,
                    status_code INT NOT NULL,
                    response_time VARCHAR(50),
                    model_predict VARCHAR(15),
                    is_right_answer BOOLEAN  
                );
            ''')
            print("Таблица 'logs' успешно создана или уже существует.")
        except Error as e:
            print(f"Ошибка при инициализации базы данных: {e}")
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    init_database()