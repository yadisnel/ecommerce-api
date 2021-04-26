# -*- coding: utf-8 -*-
import json
import os
import uuid
from typing import List
import requests
from datetime import datetime, timezone
from pydantic import BaseConfig, BaseModel


class RwModel(BaseModel):
    class Config(BaseConfig):
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        }


class UserOut(RwModel):
    id: str = None
    full_name: str = None
    primary_email: str = None
    creation_time: datetime = None
    last_login_time: datetime = None
    agreed_to_terms: bool = None
    change_password_at_next_Login: bool = None
    is_admin: bool = None


def list_accounts(event, context):
    body = {"hola": "mundo"}
    print(body)
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True
        },
        'body': body
    }


if __name__ == '__main__':
    list_accounts(None, None)
