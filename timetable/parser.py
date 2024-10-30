import os

import requests
from bs4 import BeautifulSoup
import re


class FileClass:
    path:str = ""
    name:str = ""
    link:str = ""
    last_update:str = ""

    def __init__(self, path, name, link, lastUpdate):
        self.path = path
        self.name = name
        self.link = link
        self.last_update = lastUpdate

class WebParser:
    def get_files_from_webpage(self, web_link:str, current_path:str = ""):
        '''
        Ищет на странице и в её дочерних страницах все файлы
        :param web_link: Ссылка на страницу
        :param current_path: Текущий путь к файлу
        :return: Список всех найденных файлов
        '''
        #Контейнер файлов
        files = []

        #Пытаемся получить основной контент страницы
        try:
            content = self.__get_page_content(web_link)
        except Exception as e:
            print(e)
            return files

        header3_text = ""
        header4_text = ""

        # Проходим по элементам контента
        for element in content.descendants:
            # Проверяем заголовок уровня 3
            if element.name == 'h3':
                #Запоминаем заголовок 3 урвоня
                header3_text = element.get_text(strip=True)

                # Сбрасываем header4 при нахождении нового header3
                header4_text = ""

            # Проверяем заголовок уровня 4
            elif element.name == 'h4':
                #Запоминаем заголовок 4 уровня
                header4_text = element.get_text(strip=True)

            # Ищем список гиперссылкам
            elif element.name == 'ul':
                # Формируем полный путь
                full_path = self.__add_to_path_some_elements(current_path, [header3_text, header4_text])

                # Анализируем все гиперссылкам
                for li in element.find_all('li'):
                    files += self.__find_files_from_li(li, web_link, full_path)

        # Возвращаем список всех файлов
        return files

    def __find_files_from_li(self, li, web_url, current_path):
        '''
        Получает все файлы из элемента <li>
        :param li: Элемента <li>
        :param web_url: Ссылка на текущую страницу, на которой размещён этот элемент
        :param current_path: Текущий путь к файлам
        :return: Список файлов, найденных по ссылке
        '''
        files = []
        link_tag = li.find('a', href=True)
        if link_tag:
            # Получаем имя сслыки
            link_name = link_tag.text.strip()
            # Получаем URL ссылки
            link_url = requests.compat.urljoin(web_url, link_tag['href'])

            # Проверяем, что ссылка ведёт на файл
            if self.__is_file_with_extension(link_url, ['.xls', '.xlsx', '.doc', '.docx']):
                # Извлекаем дату обновления, если она есть
                last_update = self.__get_update_time_from_text(li.text)

                # Создаем объект файла и добавляем в список
                file_obj = FileClass(current_path, self.__get_file_name(link_url), link_url, last_update)
                files.append(file_obj)

            else:
                # Добавляем новую директорию в путь
                current_path = self.__add_to_path(current_path, link_name)

                # Добавляем в список все файлы, которые только сможем найти на веб странице по этой ссылке
                files += self.get_files_from_webpage(link_url, current_path)

        # Вернуть список файлов
        return files

    def __get_page_content(self, url:str):
        '''
        Получает основной контент с Web страницы
        :param url: ссылка Web страницы
        :return: Основной контент страницы
        '''
        #Получение web страницы
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error opening web page. URL: {url}")

        #Распарсить HTML страницу сайта
        soup = BeautifulSoup(response.text, 'html.parser')

        #Получение основного контента на странице
        content_wrapper = soup.find(class_='content-wrapper')
        if not content_wrapper:
            raise Exception(f"Can't find main content on web page. URL: {url}")

        #Вернуть основной контент
        return content_wrapper

    def __get_update_time_from_text(self, text, error_text = "Неизвестно"):
        '''
        Ищет время в строке
        :param text: Строка с временем
        :param error_text: Сообщение в случае, если время не было найдено
        :return: Строка
        '''
        last_update_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', text)
        return last_update_match.group(0) if last_update_match else error_text

    def __add_to_path_some_elements(self, path, elements:list, is_file = False):
        '''
        Добавляет к уже существующему пути дополнительные пути
        :param path: Изначальный путь
        :param elements: Список элементов
        :param is_file: Последний элемент является файлом, символ '/' в конце строки не нужен 
        :return: Дополненный путь
        '''
        result_path = path
        list_length = len(elements)
        for i in range(list_length):
            result_path = self.__add_to_path(result_path, elements[i], i + 1 >= list_length and is_file)
        return result_path

    def __add_to_path(self, path, element:str, is_file = False):
        '''
        Добавляет элемент к пути
        :param path: Изначальный путь
        :param element: Следующий элемент в пути
        :param is_file: Элемент является файлом, символ '/' в конце строки не нужен 
        :return: Дополненный путь
        '''
        if element != "":
            path += element
            if not is_file:
                path += '/'
        return path

    def __is_file_with_extension(self, file_path, extensions):
        '''
        Проверяет соответствие файла одному из расширений в списке
        :param file_path: Путь к файлу
        :param extensions: Список доступных разширений
        :return: Соответствие файла расширению
        '''
        for extension in extensions:
            if file_path.endswith(extension):
                return True
        return False

    def __get_file_name(self, file_path:str):
        '''
        Возвращает имя файла
        :param file_path: Путь к файлу
        :return: Имя файла
        '''
        index = file_path.rfind('/') + 1
        return file_path[index:]


if __name__ == '__main__':
    currentPath = "Расписания/Расписание занятий/"
    webLink = "https://www.vstu.ru/student/raspisaniya/zanyatiy/"

    parser = WebParser()
    files = parser.get_files_from_webpage(webLink, currentPath)

    for file in files:
        print(f"Путь: {file.path}, Имя файла: {file.name}, Ссылка: {file.link}, Последнее обновление: {file.last_update}")

    for file in files:
        print(file.name)
