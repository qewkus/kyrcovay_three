import unittest
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import requests

from src.hh_api import HHAPI


class TestHHAPI(unittest.TestCase):
    """
    Тестовый класс для проверки функциональности класса HHAPI.
    """

    def setUp(self) -> None:
        """
        Инициализация экземпляра HHAPI перед каждым тестом.
        """
        self.api: HHAPI = HHAPI()

    @patch("requests.get")
    def test_get_companies_success(self, mock_get: Mock) -> None:
        """
        Тестирование успешного получения информации о работодателях.

        :param mock_get: Замещающий объект для requests.get.
        """
        mock_response: Mock = Mock()
        mock_response.json.return_value = {"id": 1, "name": "Company A"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        companies: List[Dict[str, Any]] = self.api.get_companies([1])

        self.assertEqual(len(companies), 1)
        self.assertEqual(companies[0]["name"], "Company A")

    @patch("requests.get")
    def test_get_companies_http_error(self, mock_get: Mock) -> None:
        """
        Тестирование обработки HTTP ошибки при получении информации о работодателях.

        :param mock_get: Замещающий объект для requests.get.
        """
        mock_get.side_effect = requests.exceptions.HTTPError("404 Client Error")

        companies: List[Dict[str, Any]] = self.api.get_companies([999])

        self.assertEqual(companies, [])

    @patch("requests.get")
    def test_get_vacancies_success(self, mock_get: Mock) -> None:
        """
        Тестирование успешного получения списка вакансий для работодателя.

        :param mock_get: Замещающий объект для requests.get.
        """
        mock_response: Mock = Mock()
        mock_response.json.return_value = {"items": [{"id": 1, "name": "Vacancy A"}]}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        vacancies: List[Dict[str, Any]] = self.api.get_vacancies(1)

        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0]["name"], "Vacancy A")

    @patch("requests.get")
    def test_get_vacancies_http_error(self, mock_get: Mock) -> None:
        """
        Тестирование обработки HTTP ошибки при получении списка вакансий.

        :param mock_get: Замещающий объект для requests.get.
        """
        mock_get.side_effect = requests.exceptions.HTTPError("404 Client Error")

        vacancies: List[Dict[str, Any]] = self.api.get_vacancies(999)

        self.assertEqual(vacancies, [])


if __name__ == "__main__":
    unittest.main()
