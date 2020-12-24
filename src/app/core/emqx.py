from src.app.core.config import broker_host, broker_port, admin_user, admin_pass
import paho.mqtt.client as mqtt
#
#
# Define the callback to handle CONNACK from the broker, if the connection created normal, the value of rc is 0
def on_connect(client, userdata, flags, rc):
    print("Connection to broker returned with result code:" + str(rc))


# Define the callback to hande publish from broker, here we simply print out the topic and payload of the received
# message
def on_message(client, userdata, msg):
    print("Received message, topic:" + msg.topic + "payload:" + str(msg.payload))


# Callback handles disconnection, print the rc value
def on_disconnect(client, userdata, rc):
    print("Connection returned result:"+ str(rc))


# Create an instance of `Client`
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect= on_disconnect
mqtt_client.on_message = on_message


async def conect_to_broker():
    mqtt_client.username_pw_set(username=admin_user, password=admin_pass)
    mqtt_client.connect_async(broker_host, broker_port, 60)
    mqtt_client.loop_start()


async def close_broker_cnx():
    mqtt_client.loop_stop()


def get_user_topic(user_id: str):
    return "users/" + user_id


def get_all_users_topic():
    return "users/all"
