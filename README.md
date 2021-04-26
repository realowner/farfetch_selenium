# Установка и запуск (Linux)

После переноса папки в нужное место, зайдите в дерикторию со скриптом и создайте виртуальное окружение:
```
python3 -m venv venv
```
После создания активируйте его:
```
source venv/bin/activate
```
После активации в терминале появится    `(venv)~#`. После этого установите зависимости:
```
python -m pip install -r requirements.txt
```
После установки зависимостей скрипт готов к запуску. 
### Запуск скрипта
Для запуска скрипта в дефолтном режиме (с установленным по умолчанию кол-вом потоков - 10) и фоновом режиме:
```
python main.py &
```
`&` - обязателен, для работы в фоне
Для изменения кол-ва потоков запустить скрипт с аргументом **-t**:
```
python main.py -t=X &
```
где X - нужное кол-во потоков
# О скрипте:

### Потоки:
Скрипт распределяет строки в БД между **10** потоками. Изменить количество потоков можно только изменяя код
### Режим работы:
Работает постоянно в фоне, не нужно перезапускать каждый раз после обновление базы
### Аккаунты и прокси:
Для парсинга с базы берутся аккаунты и прокси со статусом **1**
### Логи:
Все логи скрипта лежат в папке **logs/** корневой директории. 
В файл **global.log** записывется работа скрипта, в **thread_(номер).log*** записываются логи конкретного потока.
### Основной принцип работы
Скрипт по дефолту работает на **10** потоков. Изначально он проверяет есть ли в базе достаточно записей для проверки, если есть - скрипт запускает все треды и начинает парсинг, в ином случае скрипт спит 15 минут. Все действия потоков записываются в логи.

# Обязательные условия:
1. Минимальное кол-во прокси в базе должно быть рано или больше кол-ва потоков
2. Скрипт запустит потоки как только кол-во записей будет равнa или больше кол-ва потоков
3. Приватные прокси должны быть привязаны к ip машины
