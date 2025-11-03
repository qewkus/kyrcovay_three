






if __name__ == '__main__':
    print("Добро пожаловать в систему вакансий! \n")

    while True:
        print("Выберете действие: ")
        print("1. Создать базу и загрузить данные")
        print("2. Вывести меню работы с данными")
        print("3. Выйти\n")

        user_choice = input("Введите номер действия: ")
        if user_choice == "1":
            # database.py функционал
            pass
        elif user_choice == "2":
            # должна вызваться функция всего функционала
            pass
        elif user_choice == "3":
            print("Выход из программы")
            break
        else:
            print("Неверный номер. Введите снова.\n")