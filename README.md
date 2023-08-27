# Вакансии
# Бирюков Виктор Владимирович. Курсовой проект по курсу (5) "ООО - Объектно-ориентированное программирование"

## Парсинг вакансий по запросу профессии с HeadHunter и SuperJob (примеры: бухгалтер или программист или разработчик, повар)
> В текущую папку проекта предусмотрено скачивание(сохранение по нажатию S) json-файла скачанных вакансий разных источников

## Реализованы сортировка, фильтрация по особым ключевым словам по вводу пользователя
## (например. 1С + SQL + VBA + международн)

Скачиваются все вакансии, заранее сайтом отсортированные по убыванию зарплат, по всем валютам оклада,
с учетом конвертации по курсу ЦБ. 
Пользователь в качестве дополнительного фильтра может выбрать перечень городов вакансий, но изначально скачиваются все
регионы. Фильтрация городов и особых ключевых слов применяется уже к топ-списку зарплатных вакансий.

ПОСКОЛЬКУ ПАРСИНГ ОГРАНИЧИВАЕТСЯ числом запросов в минуту (на HH), при возникновении запроса капчи 
пользователю предлагается либо отказаться от скачивания расширенных условий-требований к кандидату,
либо нажимать Enter последовательно (при этом программно также происходит увеличение искусственной задержки на 20%
каждый раз). В случае нажатия 0 дальнейшее скачивание будет ускорено - только с пагинацией по выбранным HH страницам,
без получения расширенных полей по каждой вакансии (при этом в поиск по особым ключевым словам не попадут полные тексты
предъявляемых к кандидату требований - только "обрезанные" по числу символов до 100 примерно)
 

## Стабильная версия - на Github в ветке 'main'
- Тесты написаны на pytest (в модуле в папке tests)
- Требования дополнительных подключаемых модулей: BeautifulSoup (очистка от html-tэгов в длинных текстах), 
-    +  re (для функция переноса длинной строки текста на последующие строки при выводе на экран)