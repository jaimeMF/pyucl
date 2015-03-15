import io
import unittest

import ucl

class TestDecoder(unittest.TestCase):
    def test_decoder(self):
        ucl_conf = '''
            "author": "Jules Verne",
            "title": "Voyage au centre de la Terre",
        '''.encode('utf-8')
        expected_result = {'author': 'Jules Verne', 'title': 'Voyage au centre de la Terre'}
        result = ucl.loads(ucl_conf)
        self.assertEqual(result, expected_result)

        result = ucl.load(io.BytesIO(ucl_conf))
        self.assertEqual(result, expected_result)

        self.assertRaises(ucl.UclDecoderError, ucl.loads, b'"foo":"ds')
