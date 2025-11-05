import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def create_database(db_name: str, user: str, password: str) -> None:
    """
    Создает базу данных с указанным именем.

    :param db_name: Имя базы данных, которую необходимо создать.
    :param user: Имя пользователя для подключения к PostgreSQL.
    :param password: Пароль пользователя для подключения к PostgreSQL.
    """
    try:
        connection = psycopg2.connect(user=user, password=password, host="localhost", port="5432", dbname="postgres")
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute("DROP DATABASE IF EXISTS {};".format(db_name))
        cursor.execute(f"CREATE DATABASE {db_name};")
        print(f"База данных '{db_name}' успешно создана.")
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def create_tables(db_name: str, user: str, password: str) -> None:
    """ "
    Создает таблицы в указанной базе данных.

    :param db_name: Имя базы данных, в которой необходимо создать таблицы.
    :param user: Имя пользователя для подключения к PostgreSQL.
    :param password: Пароль пользователя для подключения к PostgreSQL.
    """
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(user=user, password=password, host="localhost", port="5432", dbname=db_name)
        cursor = connection.cursor()
        print("Подключение к базе данных успешно.")

        cursor.execute("DROP TABLE IF EXISTS vacancies;")
        cursor.execute("DROP TABLE IF EXISTS companies;")

        cursor.execute(
            """
        CREATE TABLE companies (
            hh_id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        )
        """
        )
        print("Таблица 'companies' успешно создана.")

        cursor.execute(
            """
        CREATE TABLE vacancies (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            salary_min INTEGER,
            salary_max INTEGER,
            salary_currency VARCHAR(10),
            company_id INTEGER REFERENCES companies(hh_id)
        )
        """
        )
        print("Таблица 'vacancies' успешно создана.")

        connection.commit()

    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    db_name = os.getenv("DB_NAME")  # Получаем имя базы данных из переменной окружения
    user = os.getenv("DB_USER")  # Получаем имя пользователя из переменной окружения
    password = os.getenv("DB_PASSWORD")  # Получаем пароль из переменной окружения

    if db_name is None or user is None or password is None:
        raise ValueError("Необходимо установить переменные окружения DB_NAME, DB_USER и DB_PASSWORD")

    create_database(db_name, user, password)
    create_tables(db_name, user, password)
