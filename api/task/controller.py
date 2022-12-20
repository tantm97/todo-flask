from flask import Blueprint
from flask_restful import Api

from api.task import views


task_blueprint = Blueprint('task', __name__)
task = Api(task_blueprint)

task.add_resource(views.TaskListResource,
    '/tasks/')
task.add_resource(views.TaskResource,
    '/tasks/<int:id>')
    