import requests
from bs4 import BeautifulSoup
import re


class FileClass:
    path = ""
    link = ""
    lastUpdate = ""

    def __init__(self, path, link, lastUpdate):
        self.path = path
        self.link = link
        self.lastUpdate = lastUpdate


def parser(currentPath, webLink):
    # построчно анализируем код сайта
        # если встретили блок с контетом "content-wrapper" то
            # пока не дойдём до его конца
                # ищем следующие header3 и header4 (если он есть)
                # если находим их то запоминаем каждого из них или хоия бы header3
                    # ищем неупорядочный список с ссылками
                    # если находим его то
                        # проходимся по элементам списка
                        # если название элемента заканчивается на .xls или .xlsx то
                            # добавляем имя header3, header4 (если сумели найти) и название элемента в параметр currentPath в конец строки каждого в одинарных кавычках с добавлением / без пробела после каждого
                            # создаём объект с путем, ссылкой на скачивание и последним обновлением
                            # добавляем его в конец списка с файлами (files)
                        # иначе переходим по ссылке
                            # вызываем рекурсивно функцию парсинга c обновлённой новой ссылкой (той, по которой перешли)
    # return

    # Получаем содержимое страницы
    files = []

    response = requests.get(webLink)
    if response.status_code != 200:
        print(f"Ошибка загрузки страницы: {webLink}")
        return files

    soup = BeautifulSoup(response.text, 'html.parser')

    # Ищем блок с контентом
    content_wrapper = soup.find(class_='content-wrapper')
    if not content_wrapper:
        print("Контент не найден.")
        return files

    header3_text = ""
    header4_text = ""

    # Проходим по элементам контента
    for element in content_wrapper.descendants:
        # Проверяем заголовок уровня 3
        if element.name == 'h3':
            header3_text = element.get_text(strip=True)
            header4_text = ""  # Сбрасываем header4 при нахождении нового header3

        # Проверяем заголовок уровня 4
        elif element.name == 'h4':
            header4_text = element.get_text(strip=True)

        # Ищем списки с ссылками
        elif element.name == 'ul':


            for li in element.find_all('li'):
                link_tag = li.find('a', href=True)
                if link_tag:
                    file_name = link_tag.text.strip()
                    file_link = link_tag['href']

                    next_link = requests.compat.urljoin(webLink, file_link)

                    # Проверяем, что это Excel-файл
                    if isFileWithExtension(next_link, ['.xls', '.xlsx', '.doc', '.docx']):
                        # Извлекаем дату обновления, если она есть
                        last_update_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', li.text)
                        last_update = last_update_match.group(0) if last_update_match else "Неизвестно"

                        # Формируем полный путь
                        full_path = currentPath
                        full_path = addPath(full_path, header3_text)
                        full_path = addPath(full_path, header4_text)
                        full_path = addPath(full_path, file_name)

                        # Создаем объект файла и добавляем в список
                        file_obj = FileClass(full_path, next_link, last_update)
                        files.append(file_obj)

                    else:
                        # Формируем полный путь
                        full_path = currentPath
                        full_path = addPath(full_path, header3_text)
                        full_path = addPath(full_path, header4_text)
                        full_path = addPath(full_path, file_name)

                        for file_obj in parser(full_path, next_link):
                            files.append(file_obj)

    return files

def addPath(path, nextDir):
    if nextDir != "":
        path += nextDir + '/'
    return path

def isFileWithExtension(link, extensions):
    for extension in extensions:
        if link.endswith(extension):
            return True
    return False

if __name__ == '__main__':
    currentPath = "Расписания/Расписание занятий/"
    webLink = "https://www.vstu.ru/student/raspisaniya/zanyatiy/"
    files = parser(currentPath, webLink)

    for file in files:
        print(f"Путь: {file.path[:-1]}, Ссылка: {file.link}, Последнее обновление: {file.lastUpdate}")

