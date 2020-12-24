import json
import os

from src.app.core.path import root_path

import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate(os.path.join(root_path(), 'core', 'credentials', 'firebase-admin-sdk.json'))
firebase_admin.initialize_app(cred)


def load_firebase_config():
    firebase_config = os.path.join(root_path(), 'core', 'credentials', 'firebase-admin-sdk.json')
    json_file = open(firebase_config)
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data
