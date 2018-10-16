import datetime
import random
from sanic import Sanic
from sanic.response import json,text
from sanic.views import HTTPMethodView
import asyncio
import motor.motor_asyncio


app = Sanic(__name__)

@app.listener('before_server_start')
def initDB(sanic, loop):
    client = motor.motor_asyncio.AsyncIOMotorClient(io_loop=asyncio.get_event_loop())
    employee_tracker_DB = client['employeeTracker']
    global emp_data_collect
    emp_data_collect = employee_tracker_DB['empDataAndGPS']


def serialize_employee(data):
    """delete _id and convert datetime to str"""
    del data['_id']
    if 'BirthDate' in data.keys():
        data['BirthDate'] = str(data['BirthDate'].date())
    return data


def check_fields(data):
    required_fields = ['first_name', 'last_name', 'gender', 'BirthDate', 'position']
    for field in required_fields:
        if field not in data.keys():
            return False
    return True


def str_to_datetime(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')


class Employees(HTTPMethodView):
    async def get(self,request):
        data = await emp_data_collect.find({}).to_list(20)
        for x in data:
            serialize_employee(x)
        return json(data, status=200)

    async def post(self, request):
        passed_json = request.json
        if check_fields(passed_json):
            passed_json.setdefault('middle_name','')
            passed_json.setdefault('trackingData',[])
            passed_json['BirthDate'] = str_to_datetime(passed_json['BirthDate']+' 12:00:00')
            emp_data_collect.insert_one(passed_json)
            return json({'received': True, 'message': 'employee created'}, status=201)

        return text({'received': False, 'message': 'employee not created - invalid keys'}, status=400)


class OneEmployee(HTTPMethodView):
    async def get(self,request,full_name):
        first_name, last_name = full_name.split('_')
        data = await emp_data_collect.find_one({'first_name':first_name,'last_name':last_name})
        return json(serialize_employee(data), status=200)

    async def put(self,request,full_name):
        first_name, last_name = full_name.split('_')
        passed_json = request.json
        await emp_data_collect.update_one({'first_name': first_name, 'last_name': last_name}, passed_json)
        return json({'received': True, 'message': request.json}, status=201)

    async def delete(self,request,full_name):
        first_name, last_name = full_name.split('_')
        result = await emp_data_collect.delete_one({'first_name':first_name,'last_name':last_name})
        if result.deleted_count == 1:
            return json({'deleted': True, 'message': request.json}, status=204)
        else:
            return text({'deleted': False, 'message': request.json}, status=404)


class TrackingData(HTTPMethodView):
    async def get(self,request,full_name):
        first_name, last_name = full_name.split('_')
        data = await emp_data_collect.find({'first_name': first_name, 'last_name': last_name},{'trackingData':1}).to_list(20)
        tracking_data = data[0]['trackingData']

        start_point = str_to_datetime(request.raw_args['start'])
        end_point = str_to_datetime(request.raw_args['end'])
        final_list=[]
        for struct in tracking_data:
            if (struct['time'] > start_point and struct['time'] < end_point):
                final_list.append(struct)
        return text(final_list, status=200)

    async def put(self,request,full_name):
        first_name, last_name = full_name.split('_')
        passed_list = request.json
        for json_obj in passed_list:
            json_obj['time'] = str_to_datetime(json_obj['time'])
            new_query = {'$push': {'trackingData': json_obj}}
            await emp_data_collect.update_one({'first_name': first_name, 'last_name': last_name}, new_query)
        return json({'received': True, 'message': 'insert success'},status=201)


class GenNewGPS(HTTPMethodView):
    async def put(self, request,full_name):
        first_name, last_name = full_name.split('_')
        start =[request.json['lat'], request.json['lon']]
        travel_time = datetime.datetime.strptime(request.json['travel'], '%H:%M:%S')
        travel_minute = travel_time.minute + travel_time.hour * 60
        one_minute = datetime.timedelta(minutes=1)
        new_date = str_to_datetime(request.json['time'])
        delta = 0.001553  # 100 meters in coordinates
        for i in range(travel_minute):
            start[random.randint(0, 1)] += delta
            new_date += one_minute
            new_query = {'$push' : {'trackingData' : {'time':str(new_date) , 'lat':start[0], 'lon':start[1]}}}
            await emp_data_collect.update_one({'first_name': first_name, 'last_name': last_name}, new_query)
        return json({'received': True, 'message': 'generete and insert success'}, status=201)


app.add_route(Employees.as_view(), '/tracking/api/employee')
app.add_route(OneEmployee.as_view(), '/tracking/api/employee/<full_name>')
app.add_route(TrackingData.as_view(), '/tracking/api/employee/<full_name>/trackingData')
app.add_route(GenNewGPS.as_view(), '/tracking/api/employee/<full_name>/trackingData/generateNew')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)