import json
import logging
import sys

LOG = logging.getLogger()
LOG.level = logging.DEBUG
LOG.addHandler(logging.StreamHandler(sys.stdout))


class PublicParams:
    PARAMS_FILE = './resources/params.json'

    def __init__(self):
        data = self.parse_params()
        self.frames = int(data['frames'])
        self.trace_path = data['trace_path']

    def parse_params(self):
        with open(self.PARAMS_FILE) as json_data:
            data = json.load(json_data)
            json_data.close()
        return data
