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
        self.output_new_lights(self.lights)

    def fetch_lights(self):
        data = self.fetch_resource('lights')
        return {light_id: self.fetch_light_state(light_id) for light_id in data.keys()}
    
    def fetch_light_state(self, light_id):
        light_data = self.fetch_resource('lights/{id}'.format(id=light_id))
        return {
                'name': light_data.get('name'),
                'brightness': light_data.get('state').get('bri'),
                'on': light_data.get('state').get('on'),
            }

    def poll(self):
        lights_fetched = self.fetch_lights()
        if lights_fetched != self.lights:
            lights_self_keyset = set(self.lights.keys())
            lights_fetched_keyset = set(lights_fetched.keys())

            keys_only_in_self = lights_self_keyset.difference(lights_fetched_keyset)
            keys_only_in_fetched = lights_fetched_keyset.difference(lights_self_keyset)
            keys_intersection = lights_self_keyset.intersection(lights_fetched_keyset)

            for light_id, light_data in [(key, self.lights.get(key)) for key in keys_intersection]:
                self.output_difference(light_id, lights_fetched.get(light_id))

            for light_id, light_data in [(key, self.lights.get(key)) for key in keys_only_in_self]:
                self.output_deleted_light(light_id)

            if keys_only_in_fetched:
                self.output_new_lights({light_id: lights_fetched.get(light_id) for light_id in keys_only_in_fetched})

            self.lights = lights_fetched

    def output_difference(self, fetched_light_id, fetched_light):
        for attr in self.light_state_attrs:
            if fetched_light.get(attr) != self.lights.get(fetched_light_id).get(attr):
                self.output_object({'id': fetched_light_id, attr: fetched_light.get(attr)})

    def output_new_lights(self, lights):
        self.output_object([{'id': light_id, **lights.get(light_id)} for light_id in lights])

    def output_deleted_light(self, light_id):
        self.output_object({'id': light_id, 'on': False})

    def fetch_resource(self, path):
        try:
            response = requests.get(urljoin(self.get_endpoint(), path))
            if response.status_code == 404:
                raise requests.HTTPError('Resource Not Found')
            return response.json()
        except Exception as e:
            logging.error(e)
            exit()

    def output_object(self, o):
        print(json.dumps(o, indent=4, sort_keys=True))

    def get_endpoint(self):
        base = '{scheme}://{ip}:{port}'.format(
                scheme=settings.SCHEME,
                ip=self.ip,
                port=self.port)
        url = 'api/{username}/'.format(username=settings.USERNAME)
        return urljoin(base, url)
