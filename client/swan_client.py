import json
import logging
import os
from io import IOBase

import requests

api_url = "https://preapiswan.nbfspool.com"

# task type
task_type_verified = "verified"
task_type_regular = "regular"


class SwanTask:
    def __init__(self, task_name: str, is_public: bool, is_verified: bool):
        self.task_name = task_name
        self.is_public = is_public
        self.is_verified = is_verified

    def to_request_dict(self):
        return {
            'task_name': self.task_name,
            'is_public': 1 if self.is_public else 0,
            'type': task_type_verified if self.is_verified else task_type_regular
        }


class SwanClient:
    api_token = None

    def __init__(self, api_key, access_token):
        self.api_url = api_url
        self.api_key = api_key
        self.access_token = access_token

    def refresh_token(self):
        refresh_api_token_suffix = "/user/api_keys/jwt"
        refresh_api_token_method = 'POST'

        refresh_token_url = api_url + refresh_api_token_suffix
        data = {
            "apikey": self.api_key,
            "access_token": self.access_token
        }
        try:
            resp_data = send_http_request(refresh_token_url, refresh_api_token_method, None, json.dumps(data))
            self.api_token = resp_data['jwt']
        except Exception as e:
            logging.info(str(e))
            os.exit(1)

    def post_task(self, task: SwanTask, csv: IOBase):
        create_task_url_suffix = '/tasks'
        create_task_method = 'POST'

        create_task_url = api_url + create_task_url_suffix

        payload_data = task.to_request_dict()

        csv_name = task.task_name + ".csv"
        send_http_request(create_task_url, create_task_method, self.api_token, payload_data, file=(csv_name, csv))


def send_http_request(url, method, token, payload, file=None):
    if isinstance(payload, str):
        headers = {'Content-Type': 'application/json'}
    elif isinstance(payload, dict):
        headers = {}
    else:
        headers = {}

    if token:
        headers["Authorization"] = "Bearer %s" % token

    payload_file = None
    if file:
        payload_file = {"file": file}

    with requests.request(url=url, method=method, headers=headers, data=payload, files=payload_file) as r:

        if r.status_code >= 400:
            raise Exception("response code %s " % r.status_code)
        else:
            json_body = r.json()
            if json_body['status'] != 'success':
                raise Exception("response status failed")
            else:
                return json_body['data']
