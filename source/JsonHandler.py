import json


def save(data):
    with open('SERVER_SETTINGS.json', 'w') as f:
        json.dump(data, f)


def read():
    with open('SERVER_SETTINGS.json', 'r') as f:
        return json.load(f)
