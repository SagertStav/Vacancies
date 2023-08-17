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
  while True:
    search_query = input("Введите поисковый запрос (например, бухгалтер, программист): ") # например, бухгалтер, программист?
    top_n = int(input("Введите количество вакансий для вывода в топ N: "))
    filter_words = input("Введите ключевые слова для фильтрации вакансий (через +, например, SQL+VBA): ").split("+")
  # Получение вакансий с разных платформ: сначала сохраняю в память (список экземпляров класса Vacancies, потом - в свой JSON-файл
    hh_vacancies = hh_api.get_vacancies(search_query) #"Python"
    superjob_vacancies = superjob_api.get_vacancies(search_query) #"Python"
    print(hh_vacancies)
    print(superjob_vacancies)

    filtered_vacancies = filter_vacancies(filter_words, hh_vacancies, superjob_vacancies)
    # Пользователь может вывести из файла набор вакансий по определенным критериям. Доработаю фильтр ЗП и территории работодателя
    print('Результат фильтра:', filtered_vacancies)

    if not filtered_vacancies:
        print("Нет вакансий, соответствующих заданным критериям.")
    else:
        sorted_vacancies = sort_vacancies(filtered_vacancies)
        top_vacancies = get_top_vacancies(sorted_vacancies, top_n)
        print_vacancies(top_vacancies)

    while True:
      q=input("Дальнейшие действия: - введите [S] для сохранения в файл (без фильтрации), [Q] для выхода, [М]ore - для нового запроса вакансий': \n R - для вывода результата фильтра по ранее сохраненным записям (БЕЗ ДОСТУПА К ИНТЕРНЕТ),  C - изменить критерии: ")
      if q.lower()=="q":
          break
      if q.lower() == "s":
          api_class.Vacancy.save_all_vacancies('vacancies.json')

      if q.lower() in ("сc"): #латинская/русская - неважно. Criteria
         pass #здесь реализовать смену города/области - area, с возможностью указания нескольких в маске(шаблоне) через +, а также ввод условия по ожидаемой ЗП к выводу вакансий
         return

      if q.lower() == "r": #читаем все Vacancy из старого файла
         #сначала очистим
         Vacancy.vac_list = json.loads(array)


         pass
def filter_vacancies(filter_words, hh_vacancies, superjob_vacancies):
# фильтр поставил первым аргументом, чтобы в дальнейшем реализовать возможность неограниченного списка аргументов по множеству источников получения вакансий
   #думаю вставлю простую лямбда-функцию. Тут осталось отфильтровать по ЗП, по территории/региону, которые [критерии] в настройки/константы класса можно вписать
   return api_class.Vacancy.vac_list  #доработаю применение фильтра

def sort_vacancies(vacancies:list):
    #print(vacancies)
    return vacancies #sorted(vacancies, key=lambda d: d['vac_ref']['salary_t0'])
    #return vacancies.sort()   #доработаю в классе возможность СОРТИРОВКИ ПО ЗП (+ можно по дате объявления, региону. Но тогда эти поля в классе надо объявить)

def get_top_vacancies(vacancies:list, top_n):
    return vacancies[:top_n]

def print_vacancies(vacancies:list):
    for v in vacancies:
        print(v.__str__())



if __name__ == "__main__":
    user_interaction()
