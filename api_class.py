""" В модуле описаны классы/подклассы для получения вакансий с помощью API,  а также сам класс Vacancy """
import os
from abc import ABC, abstractmethod
import requests
import json

class ApiClient(ABC):
    """Класс для получения вакансий с помощью API"""

    @abstractmethod
    def get_vacancies(self, vacancy, page=None):
        pass

class SuperJobAPI(ApiClient):
    def get_vacancies(self, vacancy, page=None):
        #secret_key = os.getenv('SJ_API_KEY')
        secret_key = 'v3.r.135704018.158d613925c599743e2547380b01b3298772c834.8bfe329dcf782914161786b30ab87c9bfc4005b3'
        url = "https://api.superjob.ru/2.0/vacancies/"
        response = requests.get(url, headers={"X-Api-App-Id": secret_key}, params={"count": 100,
                                                                                   "page": page,
                                                                                   "keyword": vacancy})
#        return response.json()["objects"]
        print(response.json()["objects"])
        for v in response.json()["objects"]:
            #убиваю двух зайцев сразу: инициализируется создаваемый экземпляр Vacancy (при этом пополняется и список этих вакансий в классе - для последующей возможности записи его в файл как дампа
            #и второе - задействую метод str()  для вывода представления экземпляра класса
           #print(Vacancy(v["name"],v["employer"]["name"], v["url"],v["salary"]["from"],v["salary"]["to"],v["salary"]["currency"]))
            print(v)

        return Vacancy.vac_list  #Да, здесь возвращаю весь искусственно комбинированный из разных источников список вакансий по запросу


class HeadHunterAPI(ApiClient):
    def get_vacancies(self, vacancy, page=None):
        url = "https://api.hh.ru/vacancies"
        params = {
            f'text': 'NAME:{vacancy}',  # Текст фильтра. В имени должно быть слово "SQL", например
#            'area': 1,  # Поиск ощуществляется по вакансиям города Москва
            'page': page,  # Индекс страницы поиска на HH
            'per_page': 100  # Кол-во вакансий на 1 странице
        }

        response = requests.get(url,  params={"count": 100, "page": page, "keyword": vacancy})
        #print(response.content.decode())  # Декодируем его ответ, чтобы Кириллица отображалась корректно - decode()
        print(response.json())
        for v in response.json()["items"]:
           print(Vacancy(v["name"],v["employer"]["name"], v["url"],v["salary"]["from"],v["salary"]["to"],v["salary"]["currency"]))

        return Vacancy.vac_list  #Да, здесь возвращаю весь искусственно комбинированный из разных источников список вакансий по запросу

class Vacancy():
   vac_list = []
# Создание класса для работы с вакансиями
# vacancy = Vacancy("Python Developer", "<https://hh.ru/vacancy/123456>", "100 000-150 000 руб.", "Требования: опыт работы от 3 лет...")
   def __init__(self, vac_name, org_where, vac_source, salary_from, salary_to,salary_currency):
       self.vac_name=vac_name
       self.org_where = org_where
       self.vac_source = vac_source
       self.salary_from = salary_from
       self.salary_to = salary_to
       self.salary_currency = salary_currency
       self.vac_list.append({"Кем":vac_name,'Куда':org_where,'Источник':vac_source,'Диапазон ЗП:':f'{self.salary_from} - {self.salary_to} {self.salary_currency}',
                                                                                                  'vac_ref':self})

   def __str__(self):
       return(f"Кем: {self.vac_name}.Куда: {self.org_where},{self.vac_source},ЗП: {self.salary_from} - {self.salary_to} {self.salary_currency}")

   def __lt__(self, other):   #для сортировки вакансий по зарплате
       return (self.salary_from if (self.salary_to==0 or self.salary_to is None) else self.salary_to) < (other.salary_from if (other.salary_to==0 or other.salary_to is None) else other.salary_to)
   def save_all_vacancies(file_name):
       with open(file_name, "w") as outfile:
           outfile.write(json.dumps(Vacancy.vac_list))    #[ob.__dict__ for ob in Vacancy.vac_list]))

   def read_vacancies_from_file(file_name):  #пожалуй, надо построчное чтение? Или в цикле создание экземпляров класса, если нужно
       Vacancy.vac_list= json.load(file_name)
       print("Прочитано из файла", Vacancy.vac_list)
       # return None
