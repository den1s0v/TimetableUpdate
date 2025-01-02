const url = 'https://185.221.153.238/timetable_params';

// Дождаться когда HTML страница загрузится
document.addEventListener('DOMContentLoaded', () => {
    // Получить первый элемент в списке
    const first_element = document.getElementById('first-select')

    addEventListenerToSelector(first_element)
});


// Функция добавления слушателя
function addEventListenerToSelector(selector) {
    selector.addEventListener('change', (event) => {
        const selectorName = event.target.name;
        const selectedValue = event.target.value;

        // Удалить все последующие селекторы
        dellSelectors(event.target)

        // Отправить запрос на сервер если выбрано значение
        if (selectedValue !== "") {
            makeRequest()
        }
    });
}

// Функция для формирования параметров
function getRequestParams() {
    const params = {}; // Объект для хранения параметров

    // Получить список элементов
    const dropdownContainer = document.getElementById('filter-container');
    const dropdownElements = dropdownContainer.querySelectorAll('select');

    // Перебираем все найденные элементы <select>
    dropdownElements.forEach(selector => {
        const name = selector.name; // Название (атрибут name)
        const value = selector.value; // Выбранное значение
        if (name && value) { // Проверяем, что оба существуют
            params[name] = value; // Добавляем в объект
        }
    });

    return params; // Возвращаем объект с параметрами
}

// Функция отправки запроса на сервер
async function makeRequest() {
    try {
        const params = getRequestParams()
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`${url}?${queryString}`)
        if (!response.ok) {
            throw new Error(`Ошибка: ${response.status}`);
        }
        const answer = await response.json();
        responseHandler(answer)
    } catch (error){
        console.error('Произошла ошибка:', error);
    }
}

// Функция обработки ответа
function responseHandler(data) {
    if (data.result === "selector") {
        // Получить список элементов
        const dropdownContainer = document.getElementById('filter-container');

        // Создаём новый селектор
        const select = document.createElement('select');
        addEventListenerToSelector(select);
        select.className = "filter-select";
        select.name = data.selector_name;

        // Создаём пустой элемент
        const option = document.createElement('option');
        option.value = '';          // Устанавливаем значение атрибута "value"
        option.disabled = true;     // Делаем опцию недоступной для выбора
        option.selected = true;     // Делаем опцию выбранной по умолчанию
        option.textContent = data.selector_description;
        select.appendChild(option);

        // Заполняем контейнер элементами
        data.selector_items.forEach(optionText => {
            const option = document.createElement('option');
            option.value = optionText;
            option.textContent = optionText;
            select.appendChild(option);
        });

        //Добавляем новый селектор
        dropdownContainer.appendChild(select)
    }
    else if (data.result === "files") {
        const container = document.getElementById("schedule-container");

        for (const fileIndex in data.files) {
            const file = data.files[fileIndex]
            const item = document.createElement('div');
            const name = document.createElement('span');
            name.className = "file-title";
            name.textContent = file.name;
            const lastUpdate = document.createElement('p');
            lastUpdate.textContent = `Дата изменения: ${file.last_update}`;
            const viewContainer = document.createElement('div');
            for (const resourceName in file.view_urls) {
                const url = file.view_urls[resourceName];
                const viewItem = document.createElement('a');
                viewItem.textContent = resourceName;
                viewItem.href = url;
                viewContainer.appendChild(viewItem);
            }
            const archiveUrl = document.createElement('a');
            archiveUrl.textContent = "Архив";
            archiveUrl.href = file.archive_urls;
            item.appendChild(name)
            item.appendChild(lastUpdate)
            item.appendChild(viewContainer)
            item.appendChild(archiveUrl)

            container.appendChild(item)
        }

    }
}

function dellSelectors(targetElement) {
    // Получить список элементов
    const dropdownContainer = document.getElementById('filter-container');

    // Флаг, после которого можно уничтожать объекты
    let flag = false
    Array.from(dropdownContainer.children).forEach((child) => {
        if (child.tagName === 'SELECT') {
            if (flag) {
                // Удаляем все <select> элементы, найденные после targetElement
                dropdownContainer.removeChild(child);
            } else if (child === targetElement){
                flag = true;
            }
        }
    });
}

// Создать список селекторов
let selectors = []
selectors.push(document.getElementById('first-select'))