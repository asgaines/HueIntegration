import unittest
import copy
import sys
import builtins
from unittest import mock

import devices

devices.print = lambda *args, **kwargs: builtins.print(*args, **kwargs)


lights = {
    '1': {
        'name': 'Light 1',
        'brightness': 100,
        'on': True,
    }, 
    '2': {
        'name': 'Light 2',
        'brightness': 200,
        'on': False,
    }, 
}


class TestIntegration(unittest.TestCase):
    valid_ip_address = '192.168.1.10'
    valid_port = 8080

    def setUp(self):
        self.lights = copy.deepcopy(lights)

    @mock.patch('devices.HueBridge.fetch_lights')
    def test_init_bridge_sets_initial_attrs(self, fetch_lights_mock):
        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        bridge = devices.HueBridge(self.valid_ip_address, self.valid_port)

        self.assertEqual(bridge.lights, self.lights)
        self.assertEqual(bridge.ip, self.valid_ip_address)
        self.assertEqual(bridge.port, self.valid_port)

    @mock.patch('devices.print')
    @mock.patch('devices.HueBridge.fetch_lights')
    def test_poll_updates_changed_name(self, fetch_lights_mock, print_mock):
        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        bridge = devices.HueBridge(self.valid_ip_address, self.valid_port)
        light_id = '1'
        
        new_name = self.lights[light_id]['name'] + ' -- updated'
        self.lights[light_id]['name'] = new_name

        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        bridge.poll()

        call_str = '{{\n    "id": "{id}",\n    "name": "{name}"\n}}'.format(id=light_id, name=new_name)
        print_mock.assert_called_with(call_str)

        self.assertEqual(bridge.lights[light_id]['name'], new_name)

    @mock.patch('devices.print')
    @mock.patch('devices.HueBridge.fetch_lights')
    def test_poll_updates_changed_brightness(self, fetch_lights_mock, print_mock):
        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        bridge = devices.HueBridge(self.valid_ip_address, self.valid_port)
        light_id = '1'
        
        new_brightness = self.lights[light_id]['brightness'] + 1
        self.lights[light_id]['brightness'] = new_brightness

        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        bridge.poll()

        call_str = '{{\n    "brightness": {brightness},\n    "id": "{id}"\n}}'.format(id=light_id, brightness=new_brightness)
        print_mock.assert_called_with(call_str)

        self.assertEqual(bridge.lights[light_id]['brightness'], new_brightness)

    @mock.patch('devices.print')
    @mock.patch('devices.HueBridge.fetch_lights')
    def test_poll_updates_changed_on_off(self, fetch_lights_mock, print_mock):
        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        bridge = devices.HueBridge(self.valid_ip_address, self.valid_port)
        light_id = '1'
        
        new_on = not self.lights[light_id]['on']
        self.lights[light_id]['on'] = new_on

        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        bridge.poll()

        bool_str = 'true' if new_on else 'false'
        call_str ='{{\n    "id": "{id}",\n    "on": {on}\n}}'.format(id=light_id, on=bool_str)
        print_mock.assert_called_with(call_str)

        self.assertEqual(bridge.lights[light_id]['on'], new_on)

    @mock.patch('devices.print')
    @mock.patch('devices.HueBridge.fetch_lights')
    def test_poll_updates_changes_when_all_changed(self, fetch_lights_mock, print_mock):
        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        bridge = devices.HueBridge(self.valid_ip_address, self.valid_port)
        light_id = '2'
        
        new_on = not self.lights[light_id]['on']
        new_brightness = self.lights[light_id]['brightness'] + 1
        new_name = self.lights[light_id]['name'] + ' -- updated'

        self.lights[light_id]['on'] = new_on
        self.lights[light_id]['brightness'] = new_brightness
        self.lights[light_id]['name'] = new_name

        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        bridge.poll()

        self.assertEqual(print_mock.call_count, 3)

        self.assertEqual(bridge.lights[light_id]['on'], new_on)
        self.assertEqual(bridge.lights[light_id]['name'], new_name)
        self.assertEqual(bridge.lights[light_id]['brightness'], new_brightness)

    @mock.patch('devices.HueBridge.fetch_lights')
    def test_lights_update_to_removed_light(self, fetch_lights_mock):
        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        bridge = devices.HueBridge(self.valid_ip_address, self.valid_port)
        
        del self.lights['1']

        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        bridge.poll()

        self.assertEqual(self.lights, bridge.lights)
        
