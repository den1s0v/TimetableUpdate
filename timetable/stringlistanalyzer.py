import re
import difflib

class StringListAnalyzer:
    """
    Класс анализа двух наборов строк.
    При анализе для каждой строки из списка строк для анализа определяется максимально похожая
    строка из списка для сравнения. Также между этими строками вычисляется коэффициент сравнения.
    """

    def __init__(self, analyze_strings:list = None, compare_strings:list = None):
        """
        Выполняет сравнение двух списков строк
        :param analyze_strings: Список строк для анализа
        :param compare_strings: Список строк для сравнения
        """
        # Создаём переменные класса
        self.__analyze_strings = [] # Список строк для анализа
        self.__compare_strings = [] # Список строк для сравнения
        self.__most_similar_strings = dict() # Словарь (строка) -> (максимально похожая строка)
        self.__max_ratio_strings = dict() # Словарь (строка) -> (степень максимальной похожести)
        self.__is_analyzed = False

        # Задаём значение спискам
        if analyze_strings is not None:
            self.set_analyze_strings(analyze_strings)
        if compare_strings is not None:
            self.set_compare_strings(compare_strings)

        # Вызов метода анализа двух наборов строк
        if analyze_strings is not None and compare_strings is not None:
            self.analyze()

    def analyze(self):
        """
        Выполняет сравнение двух списков строк
        :return: Текущий экземпляр класса
        """
        # Для каждой пары строк из списка анализируемых и сравниваемых строк
        for analyze_string in self.__analyze_strings:
            for compare_string in self.__compare_strings:
                # Рассчитать коэффициент похожести
                ratio = difflib.SequenceMatcher(None, analyze_string, compare_string).ratio()

                # Обновить значения, если текущий коэффициент больше предыдущего
                if ratio > self.__max_ratio_strings.get(analyze_string, 0):
                    self.__max_ratio_strings[analyze_string] = ratio
                    self.__most_similar_strings[analyze_string] = compare_string

        # Обновить состояние анализа
        self.__is_analyzed = True
        return self

    def set_analyze_strings(self, analyze_strings:list):
        """
        Задаёт список строк для анализа
        :param analyze_strings: Список строк для анализа
        :return: Текущий экземпляр класса
        """
        # Обновить значение
        self.__analyze_strings = analyze_strings

        # Сбросить результаты вычислений
        self.__drop_results()
        return self

    def set_compare_strings(self, compare_strings:list):
        """
        Задаёт список строк для сравнения
        :param compare_strings: Список строк для сравнения
        :return: Текущий экземпляр класса
        """
        # Обновить значение
        self.__compare_strings = compare_strings

        # Сбросить результаты вычислений
        self.__drop_results()
        return self

    def is_analyzed(self):
        """
        Проверяет, был ли выполнен анализ для данного списка строк
        :return: Результат проверки
        """
        return self.__is_analyzed

    def get_analyze_strings(self):
        """
        Возвращает список строк для анализа
        :return: Список строк
        """
        # Проверить данные на релевантность
        self.__check_results_relevance()

        # Вернуть результат
        return self.__analyze_strings

    def get_compare_strings(self):
        """
        Возвращает список строк для сравнения
        :return: Список строк для сравнения
        """
        # Проверить данные на релевантность
        self.__check_results_relevance()

        # Вернуть результат
        return self.__compare_strings

    def get_similar_string(self, string:str):
        """
        Возвращает максимально похожую строку из списка для сравнения
        :param string: Строка из списка для анализа, для которой ищется максимально похожая строка
        :return: Строка из списка для сравнения
        """
        # Проверить данные на релевантность
        self.__check_results_relevance()

        # Вернуть результат
        return self.__most_similar_strings.get(string, "")

    def get_max_compare_ratio_for_string(self, string:str):
        """
        Возвращает степень похожести для строки из списка для анализа
        :param string: Строка из списка для анализа, для которой ищется максимальная степень похожести
        :return: Степень - это число на отрезке [0,1]
        """
        # Проверить данные на релевантность
        self.__check_results_relevance()

        # Вернуть результат
        return self.__max_ratio_strings.get(string, 0)

    def get_max_ratio_words(self):
        """
        Возвращает список слов, с максимальным коэффициентом похожести
        :return: Список слов с максимальным коэффициентом похожести
        """
        # Проверить данные на релевантность
        self.__check_results_relevance()

        # Рассчитать максимальное значение коэффициента
        max_ratio = self.get_max_ratio()

        # Вернуть список слов с коэффициентом похожести, равный максимальному
        return self.get_strings_by_ratio(max_ratio)

    def get_strings_by_ratio(self, ratio:float, round_number: int | None=None):
        """
        Возвращает список строк с заданным коэффициентом похожести
        :param ratio: Коэффициент похожести
        :param round_number: Количество знаков после запятой для округления (опционально)
        :return: Список символов
        """
        # Проверить данные на релевантность
        self.__check_results_relevance()

        # Выбросить исключение, если значение округления не соответствует допустимому
        if round_number is not None and round_number < 0:
            raise Exception(f"Round number must be greater than zero. Now round number = {round_number}.")
        # Иначе убедится в степени округления коэффициента похожести
        else:
            ratio = round(ratio, round_number)

        # Список строк
        result_strings = []

        # Для каждой строки
        for string, string_ratio in self.__max_ratio_strings.items():
            #Расчёт значения коэффициента с учётом округления
            if round_number is not None:
                new_ratio = round(ratio, round_number)
            else:
                new_ratio = string_ratio

            # Добавить строку в список, если коэффициент совпадает
            if new_ratio == ratio:
                result_strings.append(string)

        # Вернуть результат
        return result_strings

    def get_strings_by_ratio_in_range(self, min_ratio:float, max_ratio:float):
        """
        Возвращает список строк с коэффициентом похожести на отрезке
        :param min_ratio: Минимальное значение коэффициента похожести
        :param max_ratio: Максимальное значение коэффициента похожести
        :return: Список строк
        """
        # Проверить данные на релевантность
        self.__check_results_relevance()

        # Список строк
        result_strings = []

        # Для каждой строки
        for string, ratio in self.__max_ratio_strings.items():
            # Добавить строку в список, если коэффициент находится в диапазоне
            if min_ratio <= ratio <= max_ratio:
                result_strings.append(string)

        # Вернуть результат
        return result_strings

    def get_max_ratio(self):
        """
        Определяет максимальную степень похожести среди всех слов
        :return: Максимальная степень похожести
        """
        # Проверить данные на релевантность
        self.__check_results_relevance()

        # Вернуть значение
        return max(self.__max_ratio_strings.keys())

    def __drop_results(self):
        """
        Сбрасывает результаты анализа
        :return: Текущий экземпляр класса
        """
        # Сброс значений
        self.__most_similar_strings = dict()
        self.__max_ratio_strings = dict()

        # Обновить состояние анализа
        self.__is_analyzed = False
        return self

    def __check_results_relevance(self):
        """
        Выбрасывает исключение, если наборы строк не проанализированны
        """
        if not self.__is_analyzed:
            raise Exception("Strings are not analyzed")