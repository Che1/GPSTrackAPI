# SanicTrackingAPI



#### Инструкция по запуску







#### Инструкция по использованию

/tracking/api/employee - методы для работы с данными сотрудников

- GET   Получить список всех сотрудников
- POST  Добавить нового сотрудника

/tracking/api/employee/<firstName_lastName> - информация о конкретном сотруднике

- GET 		Получить информацию о сотруднике
- PUT       Изменить информацию о сотруднике
- DELETE    Удалить сотрудника со всей информацией

/tracking/api/employee/<firstName_lastName>/trackingData - методы api для данных о перемещении конкретного сотрудника
- GET
- PUT 

/tracking/api/employee/<full_name>/trackingData/generateNew - метод для генерации новых точек
- PUT


firstName_lastName - имя и фамилия заглавными буквами (_прим.Alexander_Glazkov_)