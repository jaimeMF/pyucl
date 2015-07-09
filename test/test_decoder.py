from __future__ import unicode_literals

import io
import unittest

import ucl


class TestDecoder(unittest.TestCase):
    def test_decoder(self):
        ucl_conf = '''
            "author": "Jules Verne",
            "title": "Voyage au centre de la Terre",
            title_loc {
                en: "Journey to the Center of the Earth"
                es: "Viaje al centro de la Tierra"
            }
            tags: ["science fiction", "french"]
            year: 1864
            price: 23.42
            delivery_time: 3d
            available: true
            ebook: false
            webpage: null
        '''
        expected_result = {
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
            'webpage': None
        }
        result = ucl.loads(ucl_conf)
        self.assertEqual(result, expected_result)

        result = ucl.load(io.StringIO(ucl_conf))
        self.assertEqual(result, expected_result)

        self.assertRaises(ucl.UCLDecoderError, ucl.loads, '"foo":"ds')

    def test_hierarchy(self):
        ucl_conf = '''
            section "blah" {
                    key = value;
            }
            section foo {
                    key = value;
            }
        '''

        result = ucl.loads(ucl_conf)
        expected_result = {
            'section': {
                'blah': {'key': 'value'},
                'foo': {'key': 'value'},
            },
        }
        self.assertEqual(result, expected_result)

    def test_array_creation(self):
        ucl_conf = '''
            key = 1
            key = 2
        '''

        result = ucl.loads(ucl_conf)
        expected_result = {
            'key': [1, 2],
        }
        self.assertEqual(result, expected_result)
