from __future__ import unicode_literals

import io
import json
import unittest

import ucl


class TestEncoder(unittest.TestCase):
    def test_encoder(self):
        info = {
            'author': 'Jules Verne',
            'title': 'Voyage au centre de la Terre',
            'title_loc': {
                'en': 'Journey to the Center of the Earth',
                'es': 'Viaje al centro de la Tierra',
            },
            'tags': ['science fiction', 'french'],
            'year': 1864,
            'price': 23.42,
            'delivery_time': 259200.0,
            'available': True,
            'ebook': False,
            'webpage': None,
        }
        conf = ucl.dumps(info)
        new_info = ucl.loads(conf)
        self.assertEqual(new_info, info)

        buffer = io.StringIO()
        ucl.dump(info, buffer)
        new_info = ucl.loads(buffer.getvalue())
        self.assertEqual(new_info, info)

        json_repr = ucl.dumps(info, 'json')
        new_info = json.loads(json_repr)
        self.assertEqual(new_info, info)

    def test_invalid_types(self):
        wrong_key_types = {1: 'one'}
        self.assertRaises(TypeError, ucl.dumps, wrong_key_types)

        wrong_value_types = {'set': set([1, 2])}
        self.assertRaises(TypeError, ucl.dumps, wrong_value_types)
