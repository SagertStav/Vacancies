from bs4 import BeautifulSoup
import re


def includes(words_list, phrase):
 ''' Функция includes возвращает Истину, если любое из слов в любом порядке входит в проверяемый текст
 При этом если искомое словосочетание разделено *-звездочками,  требуется одновременное вхождение всех частей (AND-наличие),
 а любой отдельный элемент списка проверяется как OR-вхождение (хотя бы один) '''

 incl=True
 for i in words_list:
        if phrase is None:
            pass
        else:
            for j in i.split("*"):
                if not(j in phrase):
                   incl = False
                   break
 return incl

def income(salary_from, salary_to, income_tax):
  ''' Функция по 3-м аргументам (диапазон ЗП минимум-максимум и доля подоходного налога) возвращает доход, получаемый на руки.
    Используется для корректной сортировки вакансий, которые могут быть с выдачей ЗП 'на руки' без подоходного.
    Кроме того, в дальнейшем это поле может содержать конвертацию в рублевый эквивалент максимального ожидаемого дохода,
       если использовать зарплаты не только в рублях (hh может выдавать курс валют для этого) '''

  money_to_get =  (0 if salary_from is None or salary_from==0 else salary_from) if salary_to is None or salary_to==0 else salary_to
  money_to_get-= (money_to_get * income_tax)
  return int(money_to_get)


def RemoveHTMLTags(html_str:str)->str:  #очистка от html-tэгов в длинных текстах
#для вывода на экран предъявляемых требований к кандидату на вакансию, НЕ УСЕЧЕННЫХ API-запросом, но очищенных от html-тэгов
    return BeautifulSoup(html_str, features="html.parser").get_text()

def narrow_down_print(big_str:str):   # col_count=120): # , col_count:int):   # не пойму, почему не работает при вызове по умолчанию col_count=120
 """ Функция переноса длинной строки текста на последующие строки при выводе на экран
  big_str when printed in the command console, may exceed 80.
Characters in length and wrap around, looking ugly.
Сузим для печати на экран  границы выводимого текста """
 # Reading a single line at once:
 # for x in big_str.splitlines():
 #   print '\n'.join(line.strip() for line in re.findall(r'.{1,40}(?:\s+|$)', x))

 #print('\n'.join(line.strip() for line in re.findall(r'.{1,col_count}(?:\s+|$)', big_str)))
 print('\n'.join(line.strip() for line in re.findall(r'.{1,134}(?:\s+|$)', big_str)))
