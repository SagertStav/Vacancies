"""Критерии оценивания работы:
•	Проект выложили на GitHub.
•	Из файла README понятно, о чём проект и как его использовать.
•	В Git есть точечные коммиты.
•	Код программы грамотно разбит на функции/классы/модули/пакеты.
•	Код читабельный (хороший нейминг, есть docstring, используется typing).
•	В работе используются абстрактные классы (минимум один).
•	В работе есть переопределение магических методов.
•	Для работы с API используется библиотека requests.
•	В ходе работы программы создается файл со списком вакансий.
•	Пользователь может вывести из файла набор вакансий по определенным критериям."""

import api_class
import func

# Создание экземпляра класса для работы с API сайтов с вакансиями

hh_api = api_class.HeadHunterAPI()
superjob_api = api_class.SuperJobAPI()

# Создание экземпляра класса для работы с вакансиями
#vacancy = Vacancy("Python Developer", "<https://hh.ru/vacancy/123456>", "100 000-150 000 руб.", "Требования: опыт работы от 3 лет...")

# Сохранение информации о вакансиях в файл
#json_saver = JSONSaver()
#json_saver.add_vacancy(vacancy)
#json_saver.get_vacancies_by_salary("100 000-150 000 руб.")
#json_saver.delete_vacancy(vacancy)

# Функция для взаимодействия с пользователем
def user_interaction():
  platforms = ["HeadHunter", "SuperJob"]
  print('Получим курсы валют с HeadHunter (ждите):')
  func.narrow_down_print(str(api_class.HeadHunterAPI.get_exchange_rate()))

  while True:
    search_query = input("Введите поисковый запрос (например, бухгалтер, программист): ")
    top_n = int(input("Введите количество вакансий для вывода в топ N: "))
    town_area=input("Введите маску ГОРОДОВ поиска через + (по умолчанию = 'Москва'. Можно: Ставрополь+Волгоград):")
    town_area=('Москва' if town_area=='' else town_area).split("+")
    filter_words = input('Введите ключевые слова для фильтрации вакансий (через +, например, SQL+VBA. По умолчанию ""): ')
    filter_words = ('' if filter_words=='' else filter_words).split("+")
  # Получение вакансий с разных платформ: сначала сохраняю в память (список экземпляров класса Vacancies, потом - в свой JSON-файл
    hh_vacancies = hh_api.get_vacancies(search_query)
    #break
    superjob_vacancies = superjob_api.get_vacancies(search_query)
    #print(hh_vacancies)
    #print(superjob_vacancies)

    api_class.Vacancy.top_show(filter_words, town_area, top_n)

    while True:
      q=input("Дальнейшие действия: - введите [S] для сохранения в файл (без фильтрации), [Q] для выхода, [М]ore - для нового запроса вакансий': \n R - для вывода результата фильтра по ранее сохраненным записям (БЕЗ ДОСТУПА К ИНТЕРНЕТ),  C - изменить критерии: ")
      if q.lower()=="q":
          exit("Спасибо за внимание! До свидания!")
      if q.lower() == "s":
          api_class.Vacancy.save_all_vacancies('vacancies.json')

      if q.lower() in ("сc", "m"): #латинская/русская - неважно. Criteria
         #pass #здесь помимо смены ключевых слов можно реализовать ввод условия по ожидаемой ЗП к выводу вакансий
         break

      if q.lower() == "r": #читаем все Vacancy из старого файла
         api_class.Vacancy.read_vacancies_from_file('vacancies.json')
         api_class.Vacancy.top_show(filter_words, town_area, top_n)



if __name__ == "__main__":
    #api_class.Vacancy.read_vacancies_from_file('vacancies.json') #- чтение файла работает

    user_interaction()
