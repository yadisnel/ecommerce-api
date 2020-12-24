import json
import os

from src.app.core.path import root_path


def load_geocode_config():
    api_api_config = os.path.join(root_path(), 'core', 'credentials', 'google-geocode-api.json')
    json_file = open(api_api_config)
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data
