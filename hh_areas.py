# https://habr.com/ru/articles/666062/
# https://office-menu.ru/python/96-api-hh - это лучше
import requests      # Для запросов по API
import json          # Для обработки полученных результатов
import time          # Для задержки между запросами
import os            # Для работы с файлами
import pandas as pd  # Для формирования датафрейма с результатами
import pprint

def getAreas(regions):
    req = requests.get('https://api.hh.ru/areas')
    data = req.content.decode()
    req.close()
    jsObj = json.loads(data)
    areas = []
    for k in jsObj:
        for i in range(len(k['areas'])):
            if len(k['areas'][i]['areas']) != 0:                      # Если у зоны есть внутренние зоны
                for j in range(len(k['areas'][i]['areas'])):
                    if includes(regions, k['areas'][i]['name']) or  includes(regions, k['areas'][i]['areas'][j]['name']):
                       areas.append([k['id'],
                                  k['name'],
                                  k['areas'][i]['areas'][j]['id'],
                                  k['areas'][i]['areas'][j]['name']])
            else:                                                                # Если у зоны нет внутренних зон
                if includes(regions, k['areas'][i]['name']):
                    areas.append([k['id'],
                              k['name'],
                              k['areas'][i]['id'],
                              k['areas'][i]['name']])
    return areas

def includes(words_list, phrase):
    incl=True
    for i in words_list:

        for j in i.split("*"):
          if not(j in phrase):
             incl = False
             break
    return incl

req = requests.get('https://api.hh.ru/areas').json()
print(req)


s=input("Введите маску поиска регионов, разделяя разные области поиска знаком +, а любые символы - знаком *. Например: Волгоград*обл*+Ставр*край: ")
s=s.split("+")
print("Разделение", s)
areas = getAreas(s)

print("Ок. Рассматриваем область поиска (включая подчиненные): ")
print(areas)
