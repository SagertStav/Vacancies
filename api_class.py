""" В модуле описаны классы/подклассы для получения вакансий с помощью API,  а также сам класс Vacancy """
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import requests
import os
import time
import json
import pandas as pd

import func
import sys

class ApiClient(ABC):
    """Класс для получения вакансий с помощью API"""
    exchange_rate = {} #курс валют возьму с hh
    request_count=0
    time_before_delay:datetime=datetime.now()+timedelta(seconds=1)
    def parsing_delay(self, req_per_sec:int):
        ''' Функция притормаживания для API-запросов'''

        self.request_count+=1
        if self.request_count==req_per_sec-1:
            self.request_count=0
            print(pd.to_datetime( self.time_before_delay), pd.to_datetime(datetime.now() ),  self.time_before_delay)
            if pd.to_datetime( self.time_before_delay)>pd.to_datetime(datetime.now()):
                time.sleep((self.time_before_delay-datetime.now()).total_seconds())
            self.time_before_delay =datetime.now()+timedelta(seconds=req_per_sec)




    @abstractmethod

    def get_vacancies(self, vacancy, page=None):
        pass

class SuperJobAPI(ApiClient):
    def get_vacancies(self, vacancy, page=None):
        ''' Функция получения вакансий с SuperJob по строке параметров'''
        secret_key = os.environ['SJ_API_KEY']

        url = "https://api.superjob.ru/2.0/vacancies/"
        response = requests.get(url, headers={"X-Api-App-Id": secret_key},
            params={'count': 100, 'page': page,   # 'profession':vacancy,
                    'keyword': vacancy, #'currency':'rub'  - сначала не заморачиваться с конвертацией для сортировки, но уже привлек курс валют
                    'is_archive': False, # неархивные вакансии
                    'order_field':'payment'   #сразу с сортировкой по зарплате - по убыванию по умолчанию
                    })

        for v in response.json()["objects"]:
            #убиваю двух зайцев сразу: инициализируется создаваемый экземпляр Vacancy (при этом пополняется и список этих вакансий в классе - для последующей возможности записи его в файл как дампа
            #и второе - задействую метод str()  для вывода представления экземпляра класса
            sal_from =  0 if v['payment_from'] is None else v['payment_from']
            sal_to = 0 if v['payment_to'] is None else v['payment_to']

            #Создаю экземпляр класса по вакансии. При этом в классе пополняется сводный Vacancy.vac_list
            Vacancy(v['profession'], v['firm_name'], v['link'], v['payment_from'], v['payment_to'],
              int(func.income(sal_from, sal_to, 0.13)
                 / (1 if v['currency'] =='rub' else ApiClient.exchange_rate[v['currency']]) ),  # доход на руки, после налогообложения
                    v['currency'], v['town']['title'],v['vacancyRichText'])


        return Vacancy.vac_list  #Да, здесь возвращаю весь искусственно комбинированный из разных источников список вакансий по запросу


class HeadHunterAPI(ApiClient):
    time_to_sleep=0.6 #начальное время задержки в секундах, которое эволюционно увеличивваю после появления запроса капчи
    @classmethod

    def get_vacancy_requirements(self, vac_id:int)->str:
        #функция используется для докачивания требований к кандидату в необрезанном виде - по коду вакансии vac_id
        self.parsing_delay(self,HeadHunterAPI.time_to_sleep )  #каждый вызов requests будем "декорировать" притормаживанием, если это необходимо
        response = requests.get(f"https://api.hh.ru/vacancies/{vac_id}")

        if "description" in response.json():
            return response.json()['description']
        else:
            print(HeadHunterAPI.time_to_sleep, response.json())
            if input('Необходимо притормозить сейчас запросы к Hh... \nПродолжим через 10сек примерно (нажмёте Enter с паузой пару раз)? [0-прекратить скачивание неусеченных требований, Enter-продолжить]: ')=='0':
               HeadHunterAPI.time_to_sleep = 0  #Не будем уже ждать, если Hh потребует капчу?
            else:
               #time.sleep(HeadHunterAPI.time_to_sleep)
               HeadHunterAPI.time_to_sleep+= 1.2*HeadHunterAPI.time_to_sleep #увеличим задержку на 20%
               self.parsing_delay(self,10*HeadHunterAPI.time_to_sleep)  # каждый вызов requests будем "декорировать" притормаживанием, если это необходимо
            return self.get_vacancy_requirements(vac_id) #рекурсия


    @classmethod
#    @ApiClient.parsing_delay(120)
    def get_vacancies(self, vacancy, page=None):
        required:str=""
        url = "https://api.hh.ru/vacancies"

        params = {'text': vacancy,  # Текст фильтра. В имени вакансии должно быть слово "SQL", например
            # в парсинге возвращаются вакансии всех городов (для сохранения в файл)
            'page': page,  # Индекс страницы поиска на HH
            'describe_arguments' : True, #Для получения выставленных параметров в поиске вакансий необходимо в поисковом запросе на /vacancies добавить параметр describe_arguments=true.
            'only_with_salary': True, #только с зарплатой        #'host':'hh.ru',
            'salary':90000,      'per_page': 100,  # Кол-во вакансий на 1 странице
            'resume_search_order':'salary_des',
                #'id' :85767419 - пример вакансии с обрезкой текста требований ['snippet']["requirement"] к кандидату
                  #Полное описание можно смотреть через   https: // api.hh.ru / vacancies / (номер)
        }

        self.parsing_delay(self, 10*HeadHunterAPI.time_to_sleep)  # каждый вызов requests будем "декорировать" притормаживанием, если это необходимо
        response = requests.get(url,  params)
        if "items" in response.json():
            if response.json()["page"]==0:
                print(f'На HeadHunter (Hh) по названию вакансии найдено всего {response.json()["found"]} позиций, доступны {response.json()["pages"]} страниц.')
            else:
                print(f'\nС Hh скачано {len(Vacancy.vac_list):>5} вак-й. Парсинг {response.json()["page"]+1}-й страницы  из {response.json()["pages"]}. (Найдено {response.json()["found"]} вакансий)')
            # рекурсивно переберем все страницы, считывая в цикле все вакансии страницы
            for v in response.json()["items"]:
                  #Зарплата может быть не указана
                  sal_from= 0 if v["salary"] is None else 0 if v["salary"]["from"] is None else v["salary"]["from"]
                  sal_to=0 if v["salary"] is None else 0 if v["salary"]["to"] is None else v["salary"]["to"] #sal_from),
                  required="" if HeadHunterAPI.time_to_sleep==0 else HeadHunterAPI.get_vacancy_requirements(v["id"])
                  if "..." in required :   #не берет компилятор required[0..2]:  #см.  https://hh.ru/vacancy/84316743 выдает требования на разрыве
                      required=v['snippet']["requirement"]+required[3:]  #поэтому слепляю усеченные требования и расширенные полные
                  vac=Vacancy(v["name"],v["employer"]["name"], v["alternate_url"],
                    # приведу ЗП до налогообложения подоходным 13%
                    sal_from, sal_to,
                    int(func.income(sal_from, sal_to, 0 if v["salary"] is None else (0.13 if v["salary"]["gross"] else 0))
                        /(1 if v["salary"] is None else ApiClient.exchange_rate[v['salary']['currency']]) ), #доход на руки, после налогообложения
                    '' if v["salary"] is None else v["salary"]["currency"],
                          v['area']['name'],
                          #v['snippet']["requirement"] if required=="" is None else v['snippet']["requirement"],
                              v['snippet']["requirement"] if  required=="" else func.RemoveHTMLTags(required)
                          )
                  #func.narrow_down_print(f'\rС Hh уже скачана {len(Vacancy.vac_list):>4}-я вакансия: '+vac.__str__()+'\nТребования: '+"" if vac.vac_requirements is None else vac.vac_requirements)
                  print(f'\rС Hh скачана {len(Vacancy.vac_list):>4}-я вак-я: '+vac.__str__(),'\nТребования: ',  vac.vac_requirements,'\r', end='',flush=False) #end='\r')


            if page is None:
        # т.е. первый не рекурсивный вызов, вернувший по API число страниц, позволяет просмотреть рекурсивно остальные страницы со второй в цикле
                for p in range(1, response.json()["pages"]):
                  self.get_vacancies(vacancy, p) # рекурсивный вызов функции для перебора всех страниц
                print(f"C Hh всё скачано с учётом ограничений: {len(Vacancy.vac_list)} вакансий из {response.json()['pages']} страниц.")
                #print(Vacancy.vac_list)

            return Vacancy.vac_list  #Да, здесь возвращаю весь искусственно комбинированный из разных источников список вакансий по запросу

#    @my_decorator
#    def get_vacancies(*args, **kwargs):
 #       parsing_delay()

    def get_exchange_rate():
        #получение курса валют с Hh для использования сортировок по зарплате вне зависимости от валюты "оклада"
        dictionaries = requests.get('https://api.hh.ru/dictionaries').json()
        for currency in dictionaries['currency']:
           ApiClient.exchange_rate[currency['code']] = currency['rate']
        return  ApiClient.exchange_rate

class Vacancy():

   vac_list = []
# Создание класса для работы с вакансиями

   def __init__(self, vac_name, org_where, vac_source, salary_from, salary_to, income, salary_currency,area, vac_requirements:str):
       self.vac_name=vac_name
       self.org_where = org_where
       self.vac_source = vac_source
       self.salary_from = 0 if salary_from is None else salary_from
       self.salary_to = self.salary_from if salary_to is None else salary_to
       self.income = income
       self.salary_currency = salary_currency
       self.area = area
       self.vac_requirements = vac_requirements
       self.vac_list.append({"Кем":vac_name,"Куда":org_where,"Url":vac_source,
                             "З/п":f"{('<=' if salary_from is None else salary_from)} - {('...' if salary_to is None else salary_to)} {salary_currency}",
                              "Доход":income,'Где':area,
                             "Навык":"" if vac_requirements is None else func.RemoveHTMLTags(vac_requirements),
                             "Где":area,
                             "vac_ref":self})

   def __str__(self):
       # JSON требует двойных кавычек, которые будут использоваться вокруг строк и имён свойств. Одиночные кавычки недействительны. Даже одна неуместная запятая или двоеточие могут привести к сбою JSON-файла и не работать.
       return f"Кем: {self.vac_name}. Куда: {self.org_where}, {self.vac_source}, ЗП: {'<=' if self.salary_from == 0 else '>=' if self.salary_to == 0 else ''}{self.salary_from if self.salary_from > 0 else ''}{' - ' if self.salary_from and self.salary_to else ''}{('' if self.salary_to is None or self.salary_to == 0 else self.salary_to)} {self.salary_currency} Доход: {self.income}. Где: {self.area}"

   def __repr__(self):
# программное представление объекта позволит использовать только список ссылок на экземпляры в сводном списке класса vac_list[]
       return ''    #саму ссылку в списке делаю незаметной, это не  self.__str__()
   def print_vacancies(vacancies:list):
      i=0
      for v in vacancies:
         i+=1
         print(i,  v['vac_ref'])    #.__str__())

   def __lt__(self, other):   #для сортировки вакансий по зарплате
       return self.income < other.income

   def save_all_vacancies(file_name):
#JSON требует двойных кавычек, которые будут использоваться вокруг строк и имён свойств. Одиночные кавычки недействительны. Даже одна неуместная запятая или двоеточие могут привести к сбою JSON-файла и не работать.
       i=0
       with open(file_name, "w", encoding="utf-8") as outfile:
          outfile.write('[\n')
          for v in  Vacancy.vac_list:   #.vac_list[:3]: - для экспериментов
              i+=1
              v_to_save=v.copy()
              sys.stdout.write(f'\rСохраняю {i}-ю вакансию: '+ str(v_to_save))
              del v_to_save['vac_ref']
              outfile.write(json.dumps(v_to_save, indent=1, ensure_ascii=False)+(',\n' if i<len(Vacancy.vac_list) else ''))

          outfile.write(']')
          print('\n')

   def filter_vacancies(filter_words, town_area): #функция фильтрует по всему сводному списку экземпляров Vacancies
       return [x for x in Vacancy.vac_list
               if (True if filter_words=='' else (func.includes(filter_words, x['vac_ref'].vac_name) or
                   func.includes(filter_words, x['vac_ref'].vac_requirements)) )
               and func.includes(town_area, x['vac_ref'].area)]  # на самом деле

   def sort_vacancies(vacancies: list):
       # сортировка по убыванию зарплат. Бывают ЗП от 145000 руб., например, где salary_to не задано.
       # Инвалюта корректно сортируется по курсу
       return sorted(vacancies, key=lambda x: x['vac_ref'].income, reverse=True)


   def read_vacancies_from_file(file_name):
       #считывание вакансий из файла  и воспроизведение экземпляров класса Vacancy в памяти заново для осуществления выборок
       Vacancy.vac_list.clear()
       with open(file_name, 'r', encoding='utf-8') as f:  # открыли файл с данными
          vacs=json.load(f)

       for v in vacs:
           #Vacancy(*map(lambda f: f, v)) # - хотел обойтись в файле одним диапазоном ЗП, без полей from, to, CURRENCY
                                          # - тогда можно было бы краткий мэппинг использовать при инициализации из файла
           Vacancy(v['Кем'], v['Куда'], v['Url'], 0,              0,      v['Доход'] , v['З/п'], v['Где'], v['Навык'])

       print(Vacancy.vac_list)
       print(f'Загружено {len(vacs)} вакансий из файла.')


   def get_top_vacancies(vacancies:list, top_n):
       return vacancies[:top_n]


   def top_show(filter_words, town_area, top_n):
      filtered_vacancies = Vacancy.filter_vacancies(filter_words, town_area)
    # Пользователь может вывести из файла набор вакансий по определенным критериям
      if not filtered_vacancies:
        print("Нет вакансий, соответствующих заданным критериям.")
      else:
        print(f'Результат фильтра - найдено {len(filtered_vacancies)} вакансий (содержащих в себе и ключевые слова "{filter_words}"): \n',
            filtered_vacancies)
        sorted_vacancies = Vacancy.sort_vacancies(filtered_vacancies)
        top_vacancies = Vacancy.get_top_vacancies(sorted_vacancies, top_n)
        print(f'Топ-{top_n} по убыванию зарплаты (ДО НАЛОГООБЛОЖЕНИЯ; ссылки кликабельные, доход "чистыми" в рублях!):')
        Vacancy.print_vacancies(top_vacancies)

