from bson import ObjectId
from typing import Dict


def is_valid_oid(oid: str):
    try:
        ObjectId(oid)
    except:
        return False
    return True


def is_valid_message_body(body: Dict):
    # TODO implement it
    return True
