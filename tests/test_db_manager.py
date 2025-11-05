import unittest
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

from src.db_manager import DBManager


class TestDBManager(unittest.TestCase):
    """
    Класс для тестирования методов класса DBManager.
    """

    @patch("psycopg2.connect")
    def setUp(self, mock_connect: MagicMock) -> None:
        """
        Подготавливает тестовые данные и мокает соединение с базой данных.

        :param mock_connect: Мок-объект для соединения с базой данных.
        """
        self.db_params = {
            "dbname": "test_db",
            "user": "test_user",
            "password": "test_password",
            "host": "localhost",
            "port": "5432",
        }
        self.db_manager = DBManager(self.db_params)
        self.mock_cursor = MagicMock()

        mock_connect.return_value.cursor.return_value = self.mock_cursor

    def test_insert_companies(self) -> None:
        """
        Тестирует метод insert_companies класса DBManager.
        """
        companies: List[Dict[str, Any]] = [{"name": "Company A", "id": 1}, {"name": "Company B", "id": 2}]

        self.db_manager.insert_companies(companies)

        self.assertEqual(self.mock_cursor.execute.call_count, 2)

        self.mock_cursor.execute.assert_any_call(
            "INSERT INTO companies (name, hh_id) VALUES (%s, %s) ON CONFLICT (hh_id) DO NOTHING",
            ("Company A", 1),
        )

        self.mock_cursor.execute.assert_any_call(
            "INSERT INTO companies (name, hh_id) VALUES (%s, %s) ON CONFLICT (hh_id) DO NOTHING",
            ("Company B", 2),
        )

    def test_insert_vacancies(self) -> None:
        """
        Тестирует метод insert_vacancies класса DBManager.
        """
        vacancies: List[Dict[str, Any]] = [
            {"name": "Vacancy A", "salary": {"from": 50000, "to": 70000, "currency": "USD"}, "employer": {"id": 1}},
            {"name": "Vacancy B", "salary": {"from": 60000, "to": 80000, "currency": "USD"}, "employer": {"id": 2}},
            {"name": "Vacancy C", "salary": {"from": 40000, "to": 60000, "currency": "USD"}, "employer": None},
        ]

        with patch("builtins.print") as mock_print:
            self.db_manager.insert_vacancies(vacancies)

            self.assertEqual(self.mock_cursor.execute.call_count, 2)

            self.mock_cursor.execute.assert_any_call(
                "INSERT INTO vacancies (title, salary_min, salary_max, salary_currency, company_id) "
                "VALUES (%s, %s, %s, %s, (SELECT hh_id FROM companies WHERE hh_id = %s))",
                ("Vacancy A", 50000, 70000, "USD", 1),
            )

            self.mock_cursor.execute.assert_any_call(
                "INSERT INTO vacancies (title, salary_min, salary_max, salary_currency, company_id) "
                "VALUES (%s, %s, %s, %s, (SELECT hh_id FROM companies WHERE hh_id = %s))",
                ("Vacancy B", 60000, 80000, "USD", 2),
            )

            mock_print.assert_called_once_with(
                "Ошибка: 'employer' отсутствует в данных вакансии 'Vacancy C'. Пропуск..."
            )

    def test_get_companies_and_vacancies_count(self) -> None:
        """
        Тестирует метод get_companies_and_vacancies_count класса DBManager.
        """
        self.mock_cursor.fetchall.return_value = [("Company A", 2), ("Company B", 1), ("Company C", 0)]

        result = self.db_manager.get_companies_and_vacancies_count()

        self.mock_cursor.execute.assert_called_once()

        expected_result = [("Company A", 2), ("Company B", 1), ("Company C", 0)]

        self.assertEqual(result, expected_result)

    def test_get_all_vacancies(self) -> None:
        """
        Тестирует метод get_all_vacancies класса DBManager.
        """
        self.mock_cursor.fetchall.return_value = [
            ("Vacancy A", "Company A", 50000, 70000, "USD"),
            ("Vacancy B", "Company B", 60000, 80000, "USD"),
        ]

        result = self.db_manager.get_all_vacancies()

        self.mock_cursor.execute.assert_called_once()

        expected_result = [
            ("Vacancy A", "Company A", 50000, 70000, "USD"),
            ("Vacancy B", "Company B", 60000, 80000, "USD"),
        ]

        self.assertEqual(result, expected_result)

    def test_get_avg_salary(self) -> None:
        """
        Тестирует метод get_avg_salary класса DBManager.
        """
        self.mock_cursor.fetchone.return_value = [60000.0]

        result = self.db_manager.get_avg_salary()

        self.mock_cursor.execute.assert_called_once_with(
            "SELECT AVG(salary_min) FROM vacancies WHERE salary_min IS NOT NULL"
        )

        expected_result = 60000.0
        self.assertEqual(result, expected_result)

    def tearDown(self):
        self.db_manager.close()


if __name__ == "__main__":
    unittest.main()
