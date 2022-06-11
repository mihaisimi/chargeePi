import logging
import requests
from dataclasses import dataclass
from enum import Enum
import json


class ChargeStateEnum(Enum):
    DETECTED = 1
    APPROVED = 2
    CHARGING = 3
    STOPPED_BY_USER = 200
    STOPPED_BY_STATION = 403
    STOPPED_BY_ERROR = 404


@dataclass
class ChargeHandshake:
    # should be 0 for new session initiation
    id: int
    uuid: str
    chargeState: str
    kilowatts: int
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




