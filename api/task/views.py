from flask import request, make_response
from sqlalchemy.exc import SQLAlchemyError

from api.utils import authentication, pagination, http_status
from api.models import Task, User
from api.schemas import TaskSchema
from api.extension import db


task_schema = TaskSchema()


class TaskResource(authentication.AuthenticationRequiredResource):
    def get(self, id):
        task = Task.query.get_or_404(id)
        result = task_schema.dump(task)
        return result

    def patch(self, id):
        task = Task.query.get_or_404(id)
        task_dict = request.get_json(force=True)
        if 'message' in task_dict and task_dict['message'] is not None:
            task.message = task_dict['message']
        dumped_task = task_schema.dump(task)
        validate_errors = task_schema.validate(dumped_task)
        if validate_errors:
            return validate_errors, http_status.HttpStatus.bad_request_400.value
        try:
            task.update()
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error": str(e)}
            return response, http_status.HttpStatus.bad_request_400.value    

    def delete(self, id):
        task = Task.query.get_or_404(id)
        try:
            delete = task.delete(task)
            response = make_response()
            return response, http_status.HttpStatus.no_content_204.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error": str(e)}
            return response, http_status.HttpStatus.unauthorized_401.value


class TaskListResource(authentication.AuthenticationRequiredResource):
    def get(self):
        pagination_helper = pagination.PaginationHelper(
            request=request,
            query=Task.query,
            resource_for_url='task.tasklistresource',
            key_name='results',
            schema=task_schema)
        pagination_result = pagination_helper.paginate_query()
        return pagination_result

    def post(self):
        task_dict = request.get_json()
        if not task_dict:
            response = {'message': 'No input data provided'}
            return response, http_status.HttpStatus.bad_request_400.value
        errors = task_schema.validate(task_dict)
        if errors:
            return errors, http_status.HttpStatus.bad_request_400.value
        try:
            user = User.query.filter_by(name=authentication.http_auth.current_user()).first()
            task = Task(message=task_dict['message'], user=user)
            task.add(task)
            query = task.query.get(task.id)
            dump_result = task_schema.dump(query)
            return dump_result, http_status.HttpStatus.created_201.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error", str(e)}
            return response, http_status.HttpStatus.bad_request_400.value
