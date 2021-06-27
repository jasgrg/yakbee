import json
import os


class Config():
    def __init__(self):
        self.config = self.load_config_file()

    def load_config_file(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                return json.load(f)
        else:
            raise Exception('No config.json found in root of project')

