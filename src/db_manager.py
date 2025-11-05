import contextlib
from typing import Any, Dict, Generator, List, Optional

import psycopg2
from psycopg2.extensions import cursor as PsycopgCursor


class DBManager:
    """
    Класс для управления взаимодействием с базой данных PostgreSQL.
    """

    def __init__(self, db_params: Dict[str, str]):
        """
        Инициализация класса DBManager.

        :param db_params: Словарь с параметрами подключения к базе данных.
        """
        self.connection = psycopg2.connect(**db_params)

    @contextlib.contextmanager
    def cursor(self) -> Generator[PsycopgCursor, None, None]:
        """
        Контекстный менеджер для управления курсором базы данных.

        :yield: Курсор для выполнения SQL-запросов.
        """
        cursor: PsycopgCursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def create_tables(self) -> None:
        """
        Создает таблицы в базе данных, используя SQL-скрипт из файла schema.sql.
        """
        with open("schema.sql", "r") as file:
            self._execute(file.read())

    def _execute(self, query: str, params: Optional[tuple] = None) -> None:
        """
        Выполняет SQL-запрос с параметрами.

        :param query: SQL-запрос для выполнения.
        :param params: Параметры для подстановки в запрос.
        """
        with self.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()

    def insert_companies(self, companies: List[Dict[str, Any]]) -> None:
        """
        Вставляет данные о работодателях в таблицу companies.

        :param companies: Список словарей с данными о работодателях.
        """
        for company in companies:
            self._execute(
                "INSERT INTO companies (name, hh_id) VALUES (%s, %s) ON CONFLICT (hh_id) DO NOTHING",
                (company["name"], company["id"]),
            )

    def insert_vacancies(self, vacancies: List[Dict[str, Any]]) -> None:
        """
        Вставляет данные о вакансиях в таблицу vacancies.

        :param vacancies: Список словарей с данными о вакансиях.
        """
        for vacancy in vacancies:

            employer_id = vacancy.get("employer", {}).get("id") if vacancy.get("employer") else None
            if employer_id is not None:
                self._execute(
                    "INSERT INTO vacancies (title, salary_min, salary_max, salary_currency, company_id) "
                    "VALUES (%s, %s, %s, %s, (SELECT hh_id FROM companies WHERE hh_id = %s))",
                    (
                        vacancy["name"],
                        vacancy.get("salary", {}).get("from"),
                        vacancy.get("salary", {}).get("to"),
                        vacancy.get("salary", {}).get("currency"),
                        employer_id,
                    ),
                )
            else:
                print(f"Ошибка: 'employer' отсутствует в данных вакансии '{vacancy['name']}'. Пропуск...")

    def get_companies_and_vacancies_count(self) -> List[tuple]:
        """
        Получает количество вакансий для каждого работодателя.

        :return: Список кортежей, содержащих имя работодателя и количество вакансий.
        """
        with self.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.name, COUNT(v.id)
                FROM companies c
                LEFT JOIN vacancies v ON c.hh_id = v.company_id
                GROUP BY c.name
            """
            )
            return cursor.fetchall()

    def get_all_vacancies(self) -> List[tuple]:
        """
        Получает все вакансии из базы данных.

        :return: Список кортежей с данными о вакансиях.
        """
        with self.cursor() as cursor:
            cursor.execute(
                """
                SELECT v.title, c.name, v.salary_min, v.salary_max, v.salary_currency
                FROM vacancies v
                JOIN companies c ON v.company_id = c.hh_id
            """
            )
            return cursor.fetchall()

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по всем вакансиям.

        :return: Средняя зарплата как число.
        """
        with self.cursor() as cursor:
            cursor.execute("SELECT AVG(salary_min) FROM vacancies WHERE salary_min IS NOT NULL")
            return cursor.fetchone()[0]

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получает список вакансий с зарплатой выше средней.

        :return: Список вакансий, где зарплата выше средней.
        """
        avg_salary = self.get_avg_salary()
        with self.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM vacancies
                WHERE salary_min > %s
            """,
                (avg_salary,),
            )
            return cursor.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получает вакансии, содержащие ключевое слово в названии.

        :param keyword: Ключевое слово для поиска.
        :return: Список вакансий, содержащих ключевое слово.
        """
        with self.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM vacancies
                WHERE title ILIKE %s
            """,
                (f"%{keyword}%",),
            )
            return cursor.fetchall()

    def close(self) -> None:
        """
        Закрывает соединение с базой данных.
        """
        self.connection.close()
