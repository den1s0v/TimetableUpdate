const url = 'https://185.221.153.238/timetable_params';
const urlStatic = 'https://185.221.153.238/static/';

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

// Функция для формирования параметров
function getRequestParams() {
    const params = {}; // Объект для хранения параметров
    params[required_key] = required_value;

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

// Функция обработки ответа
function responseHandler(data) {
    dellFilesList()
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

        if (data.selector_items.length == 1) {
            select.style.display = 'none';
            select.selectedIndex = 1;
            makeRequest();
        }
    }
    else if (data.result === "files") {
        const container = document.getElementById("schedule-container");

        for (const fileIndex in data.files) {
            const file = data.files[fileIndex]

            const schedule_item = document.createElement('div');
            schedule_item.className = "schedule-item";

            const headerContainer = getHeaderContainer(file);

            const updateInfo = getUpdateInfo(file);

            const archiveContainer = getArchiveContainer(file);


            schedule_item.appendChild(headerContainer)
            schedule_item.appendChild(updateInfo)
            schedule_item.appendChild(archiveContainer)

            container.appendChild(schedule_item)
        }

    }
}
function getHeaderContainer(file){
    const headerContainer = document.createElement('div');
    headerContainer.className = "header-container";

    const titleContainer = document.createElement('div');
    titleContainer.className = "title-container";
    const itemTitle = document.createElement('span')
    itemTitle.className = "item-title";
    itemTitle.textContent = file.name;
    titleContainer.appendChild(itemTitle);

    const iconContainer = document.createElement('div');
    iconContainer.className = "icon-container";
    for (const resourceName in file.view_urls) {
        const link = document.createElement('a');
        link.href = file.view_urls[resourceName];

        const picture = document.createElement('img');
        picture.className = "icon";
        picture.alt = resourceName;
        picture.src = getBicIconName(picture.alt);
        link.appendChild(picture);
        iconContainer.appendChild(link);
    }

    const downloadLink = document.createElement('a');
    downloadLink.href = file.download_url;

    const downloadPicture = document.createElement('img');
    downloadPicture.className = "icon";
    downloadPicture.alt = "Скачать";
    downloadPicture.src = getBicIconName(downloadPicture.alt);
    downloadLink.appendChild(downloadPicture);
    iconContainer.appendChild(downloadLink);

    headerContainer.appendChild(titleContainer);
    headerContainer.appendChild(iconContainer);

    return headerContainer;
}

function getBicIconName(alt) {
    switch (alt) {
        case "Скачать":
            return `${urlStatic}image/big_download_icon.png`
        case "google drive":
            return `${urlStatic}image/big_gdrive_icon.png`
        case "yandex disk":
            return `${urlStatic}image/big_yadrive_icon.png`
    }
}

function getUpdateInfo(file) {
    const updateInfo = document.createElement('div');
    updateInfo.className = "update-info";
    updateInfo.textContent = "Дата изменения: ";
    const cpan = document.createElement('span');
    cpan.className = "update-date";
    cpan.textContent = file.last_update;
    updateInfo.appendChild(cpan);
    return updateInfo;
}

function getArchiveContainer(file) {
    const archiveContainer = document.createElement('div');
    archiveContainer.className = "archive-block";

    const image = document.createElement('img');
    // Добавить добавление картинки
    image.alt = "Архив";
    image.className = "archive-image";
    image.src = `${urlStatic}image/background-for-archive.png`
    archiveContainer.appendChild(image);

    const archiveIcons = document.createElement('div');
    for (const resourceName in file.archive_urls) {
        const link = document.createElement('a')
        link.href = file.archive_urls[resourceName];

        const archiveImage = document.createElement('img');
        archiveImage.alt = resourceName;
        archiveImage.src = getSmallIconName(archiveImage.alt)
        //Добавить картинку
        link.appendChild(archiveImage);
        archiveIcons.appendChild(link);
    }
    archiveContainer.appendChild(archiveIcons);

    return archiveContainer;
}

function getSmallIconName(alt) {
    switch (alt) {
        case "google drive":
            return `${urlStatic}image/small_gdrive_icon.png`
        case "yandex disk":
            return `${urlStatic}image/small_yadrive_icon.png`
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

function dellFilesList() {
    // Получить список элементов
    const filesContainer = document.getElementById('schedule-container');
     Array.from(filesContainer.children).forEach((child) => {
        if (child.tagName === 'DIV') {
            filesContainer.removeChild(child);
        }
    });
}

// Создать список селекторов
let selectors = []
selectors.push(document.getElementById('first-select'))