import json
import os

from src.app.core.path import root_path


def load_stripe_config():
    stripe_config = os.path.join(root_path(), 'core', 'credentials', 'stripe.json')
    json_file = open(stripe_config)
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data
