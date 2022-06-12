import logging
import requests
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
import json
from pprint import pprint


class ChargeStateEnum(Enum):
    DETECTED = 1
    APPROVED = 2
    CHARGING = 3
    STOPPED_BY_USER = 200
    STOPPED_BY_STATION = 403
    STOPPED_BY_ERROR = 404


@dataclass_json
@dataclass
class ChargeHandshake:
    # should be 0 for new session initiation
    id: int
    time: str
    chargeState: str
    kilowatts: float
    carPlate: str
    picture: str
    # "image/png"
    pictureContentType: str
    carUuid: str
    sessionUuid: str


def fetch_jwt_token(args, logger):
    url = args.server['url']+"/api/authenticate"
    username = args.server['username']
    password = args.server['password']

    logger.info(f"Will connect to {url} with {username}:{password}")
    params = {'password': password, 'rememberMe': True,  'username':  username}
    result = requests.post(url, json=params,  headers={"Content-Type": "application/json;charset=UTF-8", "Accept": "application/json"}, timeout=10)
    if result and result.status_code == 200:
        data = json.loads(result.content)
        return data['id_token']
    else:
        logger.error(f"Error accessing {url}, will NAN")
        return "NaN"


def get_handshake_by_id(args, jwt_token, id, logger):
    url = args.server['url']+"/api/charge-handshakes/"+id
    headers = {"Authorization": "Bearer "+jwt_token, "Accept": "application/json"}
    response = requests.get(url, headers=headers, timeout=10)
    if response and response.status_code == 200:
       charge_handshake = ChargeHandshake.from_json(response.content)
       pprint(charge_handshake)
    return charge_handshake


def send_detect_handshake(args, jwt_token, id, logger):
    url = args.server['url']+"/api/charge-handshakes/"+id
    headers = {"Authorization": "Bearer "+jwt_token, "Accept": "application/json"}
    response = requests.get(url, headers=headers, timeout=10)
    if response and response.status_code == 200:
        charge_handshake = ChargeHandshake.from_json(response.content)
        pprint(charge_handshake)
    return charge_handshake



