from typing import Any, Dict, List

import requests


class HHAPI:
    """
    Класс для взаимодействия с API hh.ru для получения информации о работодателях и вакансиях.
    """

    BASE_URL = "https://api.hh.ru"

    def get_companies(self, company_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Получает информацию о работодателях по их идентификаторам.

        :param company_ids: Список идентификаторов работодателей.
        :return: Список словарей с информацией о работодателях.
        """
        companies = []
        for company_id in company_ids:
            try:
                response = requests.get(f"{self.BASE_URL}/employers/{company_id}", timeout=5)
                response.raise_for_status()
                companies.append(response.json())
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred for company_id {company_id}: {http_err}")
            except Exception as err:
                print(f"An error occurred for company_id {company_id}: {err}")
        return companies

    def get_vacancies(self, company_id: int) -> List[Dict[str, Any]]:
        """
        Получает список вакансий для заданного идентификатора работодателя.

        :param company_id: Идентификатор работодателя.
        :return: Список вакансий (или пустой список, если вакансий нет).
        """
        vacancies = []
        try:
            response = requests.get(f"{self.BASE_URL}/vacancies?employer_id={company_id}", timeout=5)
            response.raise_for_status()
            vacancies = response.json().get("items", [])
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred for company_id {company_id}: {http_err}")
        except Exception as err:
            print(f"An error occurred for company_id {company_id}: {err}")
        return vacancies
