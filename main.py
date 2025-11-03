import os
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv

from src.db_manager import DBManager
from src.hh_api import HHAPI
from src.schema import create_database, create_tables

load_dotenv()


def main() -> None:
    """
    Главная функция для создания базы данных, таблиц и загрузки данных о работодателях и вакансиях.
    """
    db_params: Dict[str, Any] = {
        "dbname": os.getenv("DB_NAME"),  # Используем переменные окружения
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }

    try:
        create_database(db_params["dbname"], db_params["user"], db_params["password"])

    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        return

    try:
        create_tables(db_params["dbname"], db_params["user"], db_params["password"])

    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
        return

    api = HHAPI()
    db = DBManager(db_params)

    company_ids: list[int] = [11679140, 561525, 9472604, 563195, 942597, 851716, 5507752, 11619215, 10266062, 2794209]
    try:
        companies: List[Dict[str, Any]] = api.get_companies(company_ids)
        db.insert_companies(companies)
        print("Данные о компаниях успешно загружены в базу данных.")
    except Exception as e:
        print(f"Ошибка при загрузке данных о компаниях: {e}")
        return

    try:
        for company in companies:
            vacancies: List[Dict[str, Any]] = api.get_vacancies(company["id"])
            db.insert_vacancies(vacancies)
            print(f"Вакансии для компании {company['name']} успешно загружены в базу данных.")
    except Exception as e:
        print(f"Ошибка при загрузке вакансий: {e}")
        return

    user_interface(db)

    db.close()


def user_interface(db_manager: DBManager) -> None:
    """
    Функция для взаимодействия с пользователем, предоставляющая интерфейс для работы с данными.

    :param db_manager: Экземпляр DBManager для работы с базой данных.
    """
    while True:
        print("\nВыберите действие:")
        print("1. Показать количество вакансий у каждой компании")
        print("2. Показать все вакансии")
        print("3. Показать среднюю зарплату по вакансиям")
        print("4. Показать вакансии с зарплатой выше средней")
        print("5. Показать вакансии по ключевому слову")
        print("6. Выход")

        choice: str = input("Введите номер действия: ")

        if choice == "1":
            try:
                companies: List[Tuple[str, int]] = db_manager.get_companies_and_vacancies_count()
                print("\nКоличество вакансий у каждой компании:")
                for company, count in companies:
                    print(f"{company}: {count} вакансий")
            except Exception as e:
                print(f"Ошибка при получении количества вакансий: {e}")

        elif choice == "2":
            try:
                vacancies: List[Tuple[str, str, int, int, str]] = db_manager.get_all_vacancies()
                print("\nВсе вакансии:")
                for title, company, salary_min, salary_max, currency in vacancies:
                    print(f"Вакансия: {title}, Компания: {company}, Зарплата: {salary_min} - {salary_max} {currency}")
            except Exception as e:
                print(f"Ошибка при получении всех вакансий: {e}")

        elif choice == "3":
            try:
                avg_salary: float = db_manager.get_avg_salary()
                print(f"\nСредняя зарплата по вакансиям: {avg_salary}")
            except Exception as e:
                print(f"Ошибка при расчете средней зарплаты: {e}")

        elif choice == "4":
            try:
                higher_salary_vacancies: List[Dict[str, Any]] = db_manager.get_vacancies_with_higher_salary()
                print("\nВакансии с зарплатой выше средней:")
                for vacancy in higher_salary_vacancies:
                    print(vacancy)
            except Exception as e:
                print(f"Ошибка при получении вакансий с зарплатой выше средней: {e}")

        elif choice == "5":
            keyword = input("Введите ключевое слово: ")
            try:
                keyword_vacancies: List[Dict[str, Any]] = db_manager.get_vacancies_with_keyword(keyword)
                print(f"\nВакансии с ключевым словом '{keyword}':")
                for vacancy in keyword_vacancies:
                    print(vacancy)
            except Exception as e:
                print(f"Ошибка при поиске вакансий по ключевому слову: {e}")

        elif choice == "6":
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор, попробуйте еще раз.")


if __name__ == "__main__":
    main()
