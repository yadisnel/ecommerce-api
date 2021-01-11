import json
import os
from core.path import root_path


def load_config():
    aws_path_config = os.path.join(root_path(), 'core', 'credentials', 'aws.json')
    json_file = open(aws_path_config)
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data
