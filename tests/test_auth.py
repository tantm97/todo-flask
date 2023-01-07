import pytest
from flask import current_app, json, url_for

from api.utils import http_status
from api.models import Task

TEST_USER_NAME = 'test1-api'
TEST_USER_PASSWORD = 'Test@123'
MAX_TODO = 10

def get_accept_content_type_headers():
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }


def get_authentication_headers(token):
    authentication_headers = get_accept_content_type_headers()
    authentication_headers['Authorization'] = \
        'Bearer ' + token
    return authentication_headers


def test_request_without_authentication(client):
    response = client.get(
        url_for('auth.adminmanagementuserlistresource', _external=True),
        headers=get_accept_content_type_headers())
    assert response.status_code == http_status.HttpStatus.unauthorized_401.value


def create_normal_user(client, name, password, max_todo):
    url = url_for('auth.registerresource', _external=True)
    data = {'name': name, 'password': password, 'max_todo': max_todo}
    response = client.post(
        url,
        headers=get_accept_content_type_headers(),
        data=json.dumps(data)
    )
    return response


def create_task(client, message, token):
    url = url_for('task.tasklistresource', _external=True)
    data = {'message': message}
    response = client.post(
        url, 
        headers=get_authentication_headers(token),
        data=json.dumps(data))
    return response


def test_create_and_retrieve_task(client):
    create_user_response = create_normal_user(client, TEST_USER_NAME, TEST_USER_PASSWORD, MAX_TODO)
    assert create_user_response.status_code == http_status.HttpStatus.created_201.value
    task_message = "This is the test message."
    token = create_user_response.get_json()['auth_token']
    post_response = create_task(client, task_message, token)
    assert post_response.status_code == http_status.HttpStatus.created_201.value
    assert Task.query.count() == 1
    post_response_data = json.loads(post_response.get_data(as_text=True))
    assert post_response_data['message'] == task_message
    new_task_url = post_response_data['url']
    get_response = client.get(
        new_task_url,
        headers=get_authentication_headers(token)
    )
    assert get_response.status_code == http_status.HttpStatus.ok_200.value
    get_response_data = json.loads(get_response.get_data(as_text=True))
    assert get_response_data['message'] == task_message