import json
import os

from twilio.rest import Client

from src.app.core.path import root_path

s3_path_config = os.path.join(root_path(), 'core', 'credentials', 'twilio.json')
json_file = open(s3_path_config)
json_str = json_file.read()
json_data = json.loads(json_str)

# Your Account SID from twilio.com/console
account_sid = json_data['account_sid']
# Your Auth Token from twilio.com/console
auth_token = json_data['auth_token']
# Your Phone From
phone_from = json_data['phone_from']
# Client
client = Client(account_sid, auth_token)


def send_sms(to: str, body: str):
    message = client.messages.create(
        to=to,
        from_=phone_from,
        body=body)
    print(message.sid)
