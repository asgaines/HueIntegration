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

    @mock.patch('devices.print')
    @mock.patch('devices.HueBridge.fetch_lights')
    def setUp(self, fetch_lights_mock, print_mock):
        self.lights = copy.deepcopy(lights)
        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        self.bridge = devices.HueBridge(self.valid_ip_address, self.valid_port)

    def test_init_bridge_sets_initial_attrs(self):
        self.assertEqual(self.bridge.ip, self.valid_ip_address)
        self.assertEqual(self.bridge.port, self.valid_port)

    @mock.patch('devices.print')
    @mock.patch('devices.HueBridge.fetch_lights')
    def test_bridge_outputs_light_data_on_init(self, fetch_lights_mock, print_mock):
        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        new_bridge = devices.HueBridge(self.valid_ip_address, self.valid_port)
        output_actual = json.loads(print_mock.call_args[0][0])
        output_expected = [
                {
                    'brightness': 200,
                    'id': '2',
                    'name': 'Light 2',
                    'on': False
                },
                {
                    'brightness': 100,
                    'id': '1',
                    'name': 'Light 1',
                    'on': True
                },
            ]

        self.assertEqual(print_mock.call_count, 1)
        self.assertEqual(len(output_actual), len(output_expected))
        for data in output_expected:
            self.assertIn(data, output_actual)

    @mock.patch('devices.print')
    @mock.patch('devices.HueBridge.fetch_lights')
    def test_poll_updates_changed_name(self, fetch_lights_mock, print_mock):
        light_id = '1'
        
        new_name = self.lights[light_id]['name'] + ' -- updated'
        self.lights[light_id]['name'] = new_name

        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        self.bridge.poll()

        output_expected = {
                'id': light_id,
                'name': new_name
            }

        output_actual = json.loads(print_mock.call_args[0][0])

        self.assertEqual(self.bridge.lights[light_id]['name'], new_name)

    @mock.patch('devices.print')
    @mock.patch('devices.HueBridge.fetch_lights')
    def test_poll_updates_changed_brightness(self, fetch_lights_mock, print_mock):
        light_id = '1'
        
        new_brightness = self.lights[light_id]['brightness'] + 1
        self.lights[light_id]['brightness'] = new_brightness

        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        self.bridge.poll()

        output_expected = {
                'brightness': new_brightness,
                'id': light_id,
            }

        output_actual = json.loads(print_mock.call_args[0][0])

        self.assertEqual(print_mock.call_count, 1)
        self.assertEqual(output_actual, output_expected)
        self.assertEqual(self.bridge.lights[light_id]['brightness'], new_brightness)

    @mock.patch('devices.print')
    @mock.patch('devices.HueBridge.fetch_lights')
    def test_poll_updates_changed_on_off(self, fetch_lights_mock, print_mock):
        light_id = '1'
        
        new_on = not self.lights[light_id]['on']
        self.lights[light_id]['on'] = new_on

        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        self.bridge.poll()

        output_expected = {
                'id': light_id,
                'on': new_on,
            }

        output_actual = json.loads(print_mock.call_args[0][0])

        self.assertEqual(print_mock.call_count, 1)
        self.assertEqual(output_actual, output_expected)
        self.assertEqual(self.bridge.lights[light_id]['on'], new_on)

    @mock.patch('devices.print')
    @mock.patch('devices.HueBridge.fetch_lights')
    def test_poll_updates_changes_when_all_changed(self, fetch_lights_mock, print_mock):
        light_id = '2'
        
        new_on = not self.lights[light_id]['on']
        new_brightness = self.lights[light_id]['brightness'] + 1
        new_name = self.lights[light_id]['name'] + ' -- updated'

        self.lights[light_id]['on'] = new_on
        self.lights[light_id]['brightness'] = new_brightness
        self.lights[light_id]['name'] = new_name

        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        self.bridge.poll()

        self.assertEqual(print_mock.call_count, 3)

        self.assertEqual(self.bridge.lights[light_id]['on'], new_on)
        self.assertEqual(self.bridge.lights[light_id]['name'], new_name)
        self.assertEqual(self.bridge.lights[light_id]['brightness'], new_brightness)

    @mock.patch('devices.print')
    @mock.patch('devices.HueBridge.fetch_lights')
    def test_lights_update_to_removed_light(self, fetch_lights_mock):
        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        self.bridge.poll()

        output_actual = json.loads(print_mock.call_args[0][0])

        output_expected = [
                {
                    'brightness': 123,
                    'id': '3',
                    'name': 'Light 3',
                    'on': True
                }
            ]

        self.assertEqual(print_mock.call_count, 1)
        self.assertEqual(output_actual, output_expected)
        self.assertEqual(self.lights, self.bridge.lights)
        
        del self.lights['1']

        fetch_lights_mock.return_value = copy.deepcopy(self.lights)
        self.bridge.poll()

        output_expected = {
                'id': light_id,
                'on': False
            }

        output_actual = json.loads(print_mock.call_args[0][0])

        self.assertEqual(print_mock.call_count, 1)
        self.assertEqual(output_actual, output_expected)
        self.assertEqual(self.lights, self.bridge.lights)
        
