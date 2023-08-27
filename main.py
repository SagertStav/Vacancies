""" Основной модуль взаимодействия по курсовой работе по ООО по парсингу вакансий
с HH и SuperJob одновременно, с записью парсинга в JSON-файл """
import os

import api_class
import func

# Создание экземпляра класса для работы с API сайтов с вакансиями
hh_api = api_class.HeadHunterAPI()
superjob_api = api_class.SuperJobAPI()

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
    superjob_vacancies = superjob_api.get_vacancies(search_query)

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
    user_interaction()
