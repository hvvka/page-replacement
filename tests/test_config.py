import json
import logging
import sys

LOG = logging.getLogger()
LOG.level = logging.DEBUG
LOG.addHandler(logging.StreamHandler(sys.stdout))


class PublicParams:
    PARAMS_FILE: str = './resources/params.json'

    def __init__(self):
        data = parse_params(self.PARAMS_FILE)
        self.frames = int(data['frames'])
        self.refresh = int(data['refresh'])
        self.trace_path = data['trace_path']


class TableStates:

    def __init__(self, file_path: str):
        data = parse_params(file_path)
        self.states = data['states']

    def get_state(self, number: int):
        return self.states[str(number)]


def cast_bool(string: str):
    return string == 'True'


def cast_decimal_or_none(string: str):
    if string == "None":
        return None
    return int(string)


def parse_params(file_path):
    with open(file_path) as json_data:
        data = json.load(json_data)
        json_data.close()
    return data
