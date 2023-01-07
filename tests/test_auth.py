import pytest
from base64 import b64encode
from flask import current_app, json, url_for

from api.utils import http_status

TEST_USER_NAME = 'test1-api'
TEST_USER_PASSWORD = 'Test@123'

def get_accept_content_type_headers():
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }


def get_authentication_headers(token):
    authentication_headers = get_accept_content_type_headers()
    authentication_headers['Authorization'] = \
        'Bearer ' + b64encode(token.encode('utf-8')).decode('utf-8')
    return authentication_headers


def test_request_without_authentication(client):
    response = client.get(
        url_for('auth.adminmanagementuserlistresource', _external=True),
        headers=get_accept_content_type_headers())
    assert response.status_code == http_status.HttpStatus.unauthorized_401.value