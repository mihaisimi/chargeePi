import logging
import os
import argparse
import yaml
import sys
import json

from src.service import server
from src.utilities.benchmark import benchmark

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

parser = argparse.ArgumentParser("Run Chargee Station Manager")

parser.add_argument('--prod', help='if true we will use the production profile (config_prod.yml)', action='store_true')
parser.add_argument('--testApi', help='if true we will test the API', action='store_true')

args = parser.parse_args()


def main():
    prod = args.prod

    config_file = f"{__location__}/../credentials/config_dev.yml"
    if prod:
        config_file = f"{__location__}/../credentials/config_prod.yml"

    print(f"Starting the Chargee Station Manager with config file:{config_file}.")

    with open(config_file, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            args.station = config['station']
            args.server = config['server']
        except yaml.YAMLError as exc:
            print(exc)

    print(f"Station UUID:{args.station['uuid']}")

    with benchmark(logger, "fetch jwt"):
        jwt_token = server.fetch_jwt_token(args, logger)
        print(f"JWT token:{jwt_token}")

    with benchmark(logger, "get handshake by id"):
        server.get_handshake_by_id(args, jwt_token, "1", logger)

    with benchmark(logger, "send detect handshake"):
        server.send_car_detected(args, jwt_token, "TM13REV", logger)


if __name__ == "__main__":
    # noinspection PyInterpreter
    if len(logging.getLogger().handlers) > 0:
        # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
        # `.basicConfig` does not execute. Thus we set the level directly.
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format=f'%(asctime)s %(levelname)s %(message)s',
            force=True
        )
    logger = logging.getLogger()
    print("\n\n")
    main()
