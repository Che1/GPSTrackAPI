from sanic import Sanic
from sanic.response import json,text
from sanic.views import HTTPMethodView
import asyncio
import motor.motor_asyncio


app = Sanic(__name__)

def serialize_employee(data):
    """delete _id and convert datetime to str"""
    del data['_id']
    if 'BirthDate' in data.keys():
        data['BirthDate'] = str(data['BirthDate'].date())
    return data


@app.listener('before_server_start')
def init(sanic, loop):
    client = motor.motor_asyncio.AsyncIOMotorClient(io_loop=asyncio.get_event_loop())
    employee_tracker_DB = client['employeeTracker']
    global emp_data_collect
    emp_data_collect = employee_tracker_DB['empDataAndGPS']




class Employees(HTTPMethodView):
    async def get(self,request):
        data = await emp_data_collect.find({}).to_list(20)
        for x in data:
            serialize_employee(x)
        return json(data)
    async def post(self, request):
        pass


class OneEmployee(HTTPMethodView):
    async def get(self,request,full_name):
        first_name, last_name = full_name.split('_')
        data = await emp_data_collect.find_one({'first_name':first_name,'last_name':last_name})
        return json(serialize_employee(data))
    async def put(self,request,full_name):
        pass
    async def delete(self,request,full_name):
        pass



class TrackingData(HTTPMethodView):
    async def get(self,request,full_name):
        first_name, last_name = full_name.split('_')
        data = await emp_data_collect.find_one({'first_name': first_name, 'last_name': last_name},{"trackingData":1})
        return json(serialize_employee(data))

    async def put(self,request,full_name):
        first_name, last_name = full_name.split('_')
        passed_json = request.json
        new_query = {'$push': {"trackingData": passed_json}}
        await emp_data_collect.update_one({'first_name': first_name, 'last_name': last_name}, new_query)
        return json({"received": True, "message": request.json})


app.add_route(Employees.as_view(), '/tracking/api/employee')
app.add_route(OneEmployee.as_view(), '/tracking/api/employee/<full_name>')
app.add_route(TrackingData.as_view(), '/tracking/api/employee/<full_name>/trackingData')
# TODO add route to generate new coordinate at /tracking/api/employee/<full_name>/trackingData/generateNew




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000,debug=True)