''' После получения страниц со списком вакансий получим детальную информацию
по каждой вакансии. Для этого разберем JSON в полученных документах 
и для каждой вакансии обратимся к API по готовой ссылке https://api.hh.ru/vacancies/{id вакансии}?host=hh.ru 

Пример json-данных со списком вакансий
Результатом работы следующего скрипта будет являться папка vacancies, наполненная файлами с информацией по вакансиям: '''

import json
import os
import requests
import time

# Получаем перечень ранее созданных файлов со списком вакансий и проходимся по нему в цикле
for fl in os.listdir('./docs/pagination'):

    # Открываем файл, читаем его содержимое, закрываем файл
    f = open('./docs/pagination/{}'.format(fl), encoding='utf8')
    jsonText = f.read()
    f.close()

    # Преобразуем полученный текст в объект справочника
    jsonObj = json.loads(jsonText)

    # Получаем и проходимся по непосредственно списку вакансий
    for v in jsonObj['items']:

        # Обращаемся к API и получаем детальную информацию по конкретной вакансии
        req = requests.get(v['url'])
        data = req.content.decode()
        req.close()

        # Создаем файл в формате json с идентификатором вакансии в качестве названия
        # Записываем в него ответ запроса и закрываем файл
        fileName = './docs/vacancies/{}.json'.format(v['id'])
        f = open(fileName, mode='w', encoding='utf8')
        f.write(data)
        f.close()

        time.sleep(0.25)

print('Вакансии собраны')
#На этом этапе работа с API HH.ru завершается.