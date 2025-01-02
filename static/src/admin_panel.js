const csrftoken = getCookie('csrftoken');
const url = 'https://185.221.153.238/admin/';
const urlStatic = 'https://185.221.153.238/static/';
const secondsTimeWait = 300;
/*---------- ИЗМЕНЕНИЕ КОНФИГУРАЦИИ СИСТЕМЫ -----------*/

// Найти все элементы формы и кнопку
const formElements = document.querySelectorAll('#scanFrequency, #rootUrl, #authFile, #storageType');
const applyChangesButton = document.getElementById('applyChangesButton');

// Список ссылкок на скачивание снимков системы
const snapshotDownloadUrls = {};
fillSnapshotDownloadUrls();

// Сохраняем начальные значения всех полей в объект
const initialValues = {};
formElements.forEach(element => {
    if (element.type === 'file') {
        initialValues[element.id] = null; // Для файлов значение по умолчанию null
    } else {
        initialValues[element.id] = element.value; // Сохраняем текущее значение
    }
});

// Функция для проверки, изменилось ли состояние формы
function checkFormChanges() {
    let isChanged = false;

    formElements.forEach(element => {
        if (element.type === 'file') {
            // Проверяем, выбран ли файл
            if (element.files.length > 0) {
                isChanged = true;
            }
        } else {
            // Сравниваем текущее значение с исходным
            if (element.value !== initialValues[element.id]) {
                isChanged = true;
            }
        }
    });

    // Активируем или деактивируем кнопку в зависимости от изменений
    applyChangesButton.disabled = !isChanged;
}

// Добавляем обработчики событий для всех элементов
formElements.forEach(element => {
    element.addEventListener('input', checkFormChanges);
    element.addEventListener('change', checkFormChanges); // Для файлов и select
});

// Обработчик для кнопки
applyChangesButton.addEventListener('click', async () => {
    if (!applyChangesButton.disabled) {
        // Применить настройки
        debugger;
        let settingsSetCorrect = await setSettings();
        debugger;
        if (settingsSetCorrect) {
            // Обновить изменения
            applyChanges();
        }
    }
});

// Функция applyChanges
function applyChanges() {
    // После применения изменений обновляем сохранённые начальные значения
    formElements.forEach(element => {
        if (element.type === 'file') {
            initialValues[element.id] = null; // Сбрасываем значение файла
        } else {
            initialValues[element.id] = element.value; // Сохраняем текущее значение
        }
    });

    // Деактивируем кнопку после применения
    applyChangesButton.disabled = true;
}

async function setSettings() {
    debugger;
    let processes = []
    // Загрузить файл конфигурации
    const authFile = document.getElementById('authFile');
    // Отправить файл, если он есть
    if (authFile.files.length) {
        processes.push(sendAuthorizationFile());
    }

    debugger;
    // Загрузить обновлённые параметры
    const params = getSystemSettingsRequestParam()
    // Отправить параметры, если есть изменения
    if (Object.keys(params).length !== 0) {
        processes.push(sendSystemSettings(params));
    }

    debugger;
    if (processes.length === 0) {
        throw new Error("Ты нахрена меня вызвал, если нет никаких изменений!")
    }

    debugger;
    let result = await Promise.all(processes);

    debugger;
    let success = true;
    result.forEach((res) => {
        debugger;
        success = success && res;
    })
    debugger;
    if (success) {
        alert("Изменения успешно применены!");
    } else {
        alert("Не удалось применить изменения!");
    }

    return success;
}

async function sendSystemSettings(params) {
    debugger;
    // Проверить что есть изменённые параметры
    if (Object.keys(params).length === 0) {
        return null;
    }

    // Отправить запрос
    const response = await fetch(`${url}settings`,
        {
            method: 'POST', // Указываем метод запроса
            headers: {
                'Content-Type': 'application/json', // Указываем тип данных
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(params) // Преобразуем объект в JSON-строку
        })

    return response.ok;
}

function getSystemSettingsRequestParam() {
    const timeUpdate = document.getElementById('scanFrequency');
    const analyzeUrl = document.getElementById('rootUrl');
    const downloadStorage = document.getElementById('storageType');

    // Получить параметры
    params = {}
    if (timeUpdate.value !== initialValues[timeUpdate.id]) {
        params['time_update'] = timeUpdate.value;
    }
    if (analyzeUrl.value !== initialValues[analyzeUrl.id]) {
        params['analyze_url'] = analyzeUrl.value;
    }
    if (downloadStorage.value !== initialValues[downloadStorage.id]) {
        params['download_storage'] = downloadStorage.value;
    }

    return params;
}

async function sendAuthorizationFile() {
    const authFile = document.getElementById('authFile');
    const file = authFile.files[0];

    // Проверяем, что файл имеет расширение .json
    if (!file.name.endsWith('.json')) {
        return false;
    }

    // Создаём FormData для отправки файла
    const formData = new FormData();
    formData.append('file', file);

    // Отправляем файл на сервер
    const response = await fetch(`${url}google_auth`, {
        method: 'PUT', // Указываем метод PUT
        headers: {
            'Content-Type': 'application/json', // Указываем тип данных
            'X-CSRFToken': csrftoken
        },
        body: await file.text() // Читаем содержимое файла как текст и отправляем
    });

    return response.ok;
}

/*---------- ПОЛУЧЕНИЕ СОСТОЯНИЯ СИСТЕМЫ -----------*/

async function getSnapshot() {
    const snapshotType = document.getElementById('snapshotType').value;
    const spinner = document.getElementById('snapshotSpinner');
    const downloadButton = document.getElementById('downloadButton');

    // Скрываем кнопку "Скачать" и показываем спиннер
    downloadButton.style.display = 'none';
    spinner.style.display = 'block';

    // Создать тело запроса
    let params = new URLSearchParams();
    params.append('action', 'make_new');
    params.append('snapshot', snapshotType);

    // Делаем запрос на создание нового снимка и получаем id процесса
    const processId = await makePostResponse('snapshot', params);

    debugger;
    // Дождаться получения снимка если есть id процесса
    if (processId !== null) {
        let time = new Date(); // Время начала изготовления списка
        let newURL = "" // Новая URL

        // Проверять состояние процесса создания файла до истечения таймаута или пока файл не найден
        while (((new Date()) - time)/1000 < secondsTimeWait && newURL === "") {
            debugger;
            // Повторный запрос
            newURL = await getSnapshotUrl(processId);
            if (newURL !== "" && newURL !== null) {
                snapshotDownloadUrls[snapshotType] = newURL;
            }

            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        if (newURL !== "" && newURL !== null) {
            alert(`Снимок "${snapshotType}" создан и готов к загрузке!`);
        }
        else {
            debugger;
            alert(`Не удалось создать снимок "${snapshotType}"! Можно скачать предыдущий.`);
        }

        spinner.style.display = 'none'; // Скрываем спиннер
        if (snapshotDownloadUrls[snapshotType] === "") {
            downloadButton.style.display = 'none'; // Скрываем кнопку "Скачать"
        }
        else {
            downloadButton.style.display = 'block'; // Показываем кнопку "Скачать"
        }
    }
}

async function getSnapshotUrl(processId) {
    // Отправить запрос
    const response = await fetch(`${url}snapshot?process_id=${processId}`);

    // Завершить выполнение, если ответ некорректный
    if (response.ok) {
        // Обработать ответ
        const data = await response.json();
        if (data?.status === "success") {
            return data?.result?.url;
        }
        else if (data?.status === "error") {
            alert (data?.result?.error_message);
        }
        else if (data?.status === "running"){
            return "";
        }
    }

    return null;
}

async function fillSnapshotDownloadUrls() {
    const snapshotTypeSelector = document.getElementById('snapshotType')
    for (const option of Array.from(snapshotTypeSelector.options)) {
        snapshotDownloadUrls[option.label] = await getLastSnapshotUrl(option.label);
    }
}

async function getLastSnapshotUrl(snapshot) {
    // Отправить запрос
    const response = await fetch(`${url}snapshot?snapshot_type=${snapshot}`);

    // Завершить выполнение, если ответ некорректный
    if (!response.ok) {
        return null;
    }

    return response.json().url;
}

// Найти элементы
const snapshotTypeSelect = document.getElementById('snapshotType');
const getSnapshotButton = document.getElementById('getSnapshotButton');
const downloadButton = document.getElementById('downloadButton');

// Обработчик скрытия кнопки "Скачать" при изменении списка
snapshotTypeSelect.addEventListener('change', () => {
    // скрыть кнопку, если нет ссылки для скачивания
    const url = snapshotDownloadUrls[snapshotTypeSelect.value];
    if (url === "" || url === undefined) {
        downloadButton.style.display = 'none'; // Скрыть кнопку "Скачать"
    }
    else {
        downloadButton.style.display = 'block';
    }
});

downloadButton.addEventListener('click', () => {
    const url = snapshotDownloadUrls[snapshotTypeSelect.value];
    const fileName = url.split('/').pop();

    downloadFile(`${urlStatic}${url}`, fileName);
});


/*---------- ОЧИСТКА СИСТЕМЫ -----------*/

// Функция для обработки кнопки "Очистить"
function requestDataCleansing() {
    // Получаем текст выбранного элемента
    const dataLocationSelect = document.getElementById('dataLocation');
    const spinner = document.getElementById('dataCleanSpinner');
    const selectedOptionText = dataLocationSelect.options[dataLocationSelect.selectedIndex].text;

    // Показываем окно подтверждения
    const isConfirmed = window.confirm(`Вы уверены, что хотите очистить: ${selectedOptionText.toLowerCase()}?`);

    // Если пользователь нажал "OK", выполняем очистку
    if (isConfirmed) {
        spinner.style.display = 'block';
        dellData()
        alert("Происходит очистка. Пожалуйста подождите."); // Сообщение о начале очистки

    } else {
        spinner.style.display = 'none';
        // Если пользователь нажал "Отмена", ничего не делаем
        alert("Очистка отменена.");
    }
}


async function dellData() {
    const dataLocationSelect = document.getElementById('dataLocation');
    const component = dataLocationSelect.value;
    // Создать тело запроса
    let params = new URLSearchParams();
    params.append('action', 'dell');
    params.append('component', component);

    // Делаем запрос на создание нового снимка и получаем id процесса
    const processId = await makePostResponse('manage_storage', params);

    // Дождаться получения снимка если есть id процесса
    if (processId !== null) {
        let time = new Date(); // Время начала изготовления списка
        let success = null

        // Проверять состояние процесса создания файла до истечения таймаута или пока файл не найден
        while (((new Date()) - time)/1000 < secondsTimeWait && success === null) {
            debugger;
            // Повторный запрос
            success = await getDellResult(processId)
            // Ожидание
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        if (success === true) {
            alert(`Очистка: "${component.toLowerCase()}" завершена успешно!`);
        }
        else {
            alert(`Не удалось завершить очистку: "${component.toLowerCase()}"!`);
        }
    }

    const spinner = document.getElementById('dataCleanSpinner');
    spinner.style.display = 'none';
}

async function getDellResult(processId) {
    // Отправить запрос
    const response = await fetch(`${url}manage_storage?process_id=${processId}`);

    // Завершить выполнение, если ответ некорректный
    if (response.ok) {
        // Обработать ответ
        const data = await response.json();
        if (data?.status === "success") {
            return true
        }
        else if (data?.status === "error") {
            alert (data?.result?.error_message);
            return false;
        }
    }

    return null;
}


// Функция для получения CSRF-токена из cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function makeResponse(url_dir, responseType, params) {
    // Отправить запрос
    return fetch(`${url}${url_dir}`,
        {
            method: responseType, // Указываем метод запроса
            headers: {
                'Content-Type': 'application/json', // Указываем тип данных
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(params) // Преобразуем объект в JSON-строку
        })
}

function downloadFile(url, filename) {
    const link = document.createElement('a'); // Создаем элемент <a>
    link.href = url; // Указываем ссылку на файл
    link.download = filename; // Указываем имя файла для скачивания

    // Добавляем элемент в DOM и инициируем скачивание
    document.body.appendChild(link);
    link.click();

    // Удаляем элемент из DOM
    document.body.removeChild(link);
}

async function makePostResponse(nextUrl, params) {
    // Отправить запрос
    const response = await fetch(`${url}${nextUrl}`,
        {
            method: 'POST', // Указываем метод запроса
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded', // Указываем тип данных
                'X-CSRFToken': csrftoken,
            },
            body:  params.toString() // Преобразуем объект в JSON-строку
        })

    // Завершить выполнение, если ответ некорректный
    if (!response.ok) {
        return null;
    }

    // Распарсить ответ и вернуть номер процесса
    const data = await response.json();

    // Вернуть ID процесса, если снимок принят в работу.
    return data?.id;
}