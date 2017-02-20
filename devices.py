import requests
import json
import socket
import logging
from urllib.parse import urljoin
from collections import namedtuple

import settings


class HueBridge():
    light_state_attrs = [
        'name',
        'brightness',
        'on',
    ]

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.lights = self.fetch_lights()

    def fetch_lights(self):
        data = self.fetch_resource('lights')
        return {light_id: self.fetch_light_state(light_id) for light_id in data.keys()}
    
    def fetch_light_state(self, light_id):
        light_data = self.fetch_resource('lights/{id}'.format(id=light_id))
        return dict(name=light_data.get('name'), 
                brightness=light_data.get('state').get('bri'),
                on=light_data.get('state').get('on'))

    def print_data(self):
        lights = [{'id': light_id, **self.lights.get(light_id)} for light_id in self.lights]
        print(json.dumps(lights, indent=4))

    def poll(self):
        lights = self.fetch_lights()
        for light_id, light in lights.items():
            self.print_difference(light_id, light)
        self.lights = lights

    def print_difference(self, new_light_id, new_light):
        if self.lights.get(new_light_id):
            for attr in self.light_state_attrs:
                if new_light.get(attr) != self.lights.get(new_light_id).get(attr):
                    print(json.dumps({'id': new_light_id, attr: new_light.get(attr)}, indent=4, sort_keys=True))

    def fetch_resource(self, path):
        try:
            response = requests.get(urljoin(self.get_endpoint(), path))
            if response.status_code == 404:
                raise requests.HTTPError('Resource Not Found')
            return response.json()
        except Exception as e:
            logging.error(e)
            exit()

    def get_endpoint(self):
        base = '{scheme}://{ip}:{port}'.format(
                scheme=settings.SCHEME,
                ip=self.ip,
                port=self.port)
        url = 'api/{username}/'.format(username=settings.USERNAME)
        return urljoin(base, url)
