# GPSTrackAPI




#### Инструкция по запуску

На сервере должен быть установлен python3.5+ c модулями sanic, motor. Если MongoDB работает локально со стандартными настройкми хоста:порта то ничего менять не надо
Менять настройки подключения к БД только в исходном файле.
Выполнить:
`python -m sanic server.app --host=0.0.0.0 --port=1337`
для запуска на указанном хосту и порту.


#### Инструкция по использованию

Все методы принимают или возвращают JSON

`/tracking/api/employee` - методы для работы с данными сотрудников

- GET   Получить список всех сотрудников
- POST  Добавить нового сотрудника

`/tracking/api/employee/<firstName_lastName>` - информация о конкретном сотруднике
``` json
{
    "first_name" : "Martin",
    "middle_name" : "Broxah",
    "last_name" : "Brock-Pedersen",
    "gender" : "male",
    "BirthDate": "1993-03-07",
    "position" : "Bot Laner",
    "trackingData": []
}
```


- GET 		Получить информацию о сотруднике
- PUT       Изменить информацию о сотруднике
- DELETE    Удалить сотрудника со всей информацией

`/tracking/api/employee/<firstName_lastName>/trackingData` - методы api для данных о перемещении конкретного сотрудника
``` json
[
{
    "time" : "2018-3-3 11:59:59",
    "lat" : 55.05,
    "lon" : 61.4,
}, 
...
]
```
- GET Запрос с параметрами start и stop в формате "1994-03-24 17:00:00". Возвращает список JSON с точками в заданном промежутке. Работает во временной зоне сервера, полученные данные переводит в GMT
- PUT Добавить несколько точек. Принимает список структур как на примере выше.

`/tracking/api/employee/<firstName_lastName>/trackingData/generateNew` - метод для генерации новых точек
- PUT генерирует и пишет в базу новые точки. Принимает структуру:

``` json 
{"time":"2018-12-30 14:20:35",
"lat":35.23,
"lon":129.12,
"travel":"00:10:00"
}
```



firstName_lastName - имя и фамилия заглавными буквами (_прим.Alexander_Glazkov_)