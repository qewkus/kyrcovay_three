import os
import unittest
from typing import Optional

import psycopg2
from dotenv import load_dotenv

from src.schema import create_database, create_tables

load_dotenv()


class TestDatabaseFunctions(unittest.TestCase):
    """
    Класс тестов для проверки функций работы с базой данных.
    """

    user: Optional[str]
    password: Optional[str]
    test_db_name: str

    @classmethod
    def setUpClass(cls) -> None:
        """
        Метод для настройки тестового окружения перед запуском тестов.
        Создает тестовую базу данных.
        """
        cls.user = os.getenv("DB_USER")
        cls.password = os.getenv("DB_PASSWORD")
        cls.test_db_name = "test_db"

        if cls.user is None or cls.password is None:
            raise ValueError("User and password cannot be None")

        create_database(cls.test_db_name, cls.user, cls.password)

    def test_create_tables(self) -> None:
        """
        Тест для проверки создания таблиц в тестовой базе данных.
        """
        connection: Optional[psycopg2.extensions.connection] = None
        cursor: Optional[psycopg2.extensions.cursor] = None

        try:

            if self.user is None or self.password is None:
                raise ValueError("User and password cannot be None")

            create_tables(self.test_db_name, self.user, self.password)

            connection = psycopg2.connect(
                user=self.user, password=self.password, host="localhost", port="5432", dbname=self.test_db_name
            )
            cursor = connection.cursor()

            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'companies');")
            companies_exists = cursor.fetchone()[0]
            self.assertTrue(companies_exists, "Таблица 'companies' не была создана.")

            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'vacancies');")
            vacancies_exists = cursor.fetchone()[0]
            self.assertTrue(vacancies_exists, "Таблица 'vacancies' не была создана.")

        except Exception as e:
            self.fail(f"Возникла ошибка при тестировании создания таблиц: {e}")
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Метод для очистки тестового окружения после выполнения тестов.
        Удаляет тестовую базу данных.
        """
        connection: Optional[psycopg2.extensions.connection] = None
        cursor: Optional[psycopg2.extensions.cursor] = None
        try:
            connection = psycopg2.connect(
                user=cls.user, password=cls.password, host="localhost", port="5432", dbname="postgres"
            )
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS {cls.test_db_name};")

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


if __name__ == "__main__":
    unittest.main()
