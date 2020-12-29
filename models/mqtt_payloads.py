from models.rwmodels import RwModel


class MqttPayload(RwModel):
    payload_type: str = None
    payload: str = None
