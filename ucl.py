from _ucl import ffi, lib as _ucl


class UCLError(Exception):
    pass


class UCLDecoderError(UCLError):
    pass


class UCLConversionError(UCLError):
    pass


def _iter_ucl_object(obj):
    iterator = _ucl.ucl_object_iterate_new(obj)
    try:
        while True:
            cur = _ucl.ucl_object_iterate_safe(iterator, True)
            if cur == ffi.NULL:
                break
            yield cur
    finally:
        _ucl.ucl_object_iterate_free(iterator)


def _convert_ucl_object(obj):
    if obj.type == _ucl.UCL_OBJECT:
        res = {}
        for child in _iter_ucl_object(obj):
            key = ffi.string(_ucl.ucl_object_key(child)).decode('utf-8')
            value = _convert_ucl_object(child)
            res[key] = value
        return res
    elif obj.type == _ucl.UCL_ARRAY:
        return [_convert_ucl_object(entry) for entry in _iter_ucl_object(obj)]
    elif obj.type == _ucl.UCL_INT:
        return _ucl.ucl_object_toint(obj)
    elif obj.type in [_ucl.UCL_FLOAT, _ucl.UCL_TIME]:
        return _ucl.ucl_object_todouble(obj)
    elif obj.type == _ucl.UCL_STRING:
        return ffi.string(_ucl.ucl_object_tostring(obj)).decode('utf-8')
    elif obj.type == _ucl.UCL_BOOLEAN:
        return bool(_ucl.ucl_object_toboolean(obj))
    elif obj.type == _ucl.UCL_NULL:
        return None
    else:
        raise UCLConversionError(
            'Unsupported object type: {}'.format(obj.type))


class UCLDecoder(object):
    def __init__(self):
        self._parser = ffi.gc(_ucl.ucl_parser_new(0), _ucl.ucl_parser_free)

    def _check_error(self):
        error = _ucl.ucl_parser_get_error(self._parser)
        if error != ffi.NULL:
            raise UCLDecoderError(ffi.string(error))

    def _get_result(self):
        obj = _ucl.ucl_parser_get_object(self._parser)
        return _convert_ucl_object(obj)

    def decode(self, s):
        _ucl.ucl_parser_add_string(self._parser, s, len(s))
        self._check_error()
        return self._get_result()


def loads(s):
    decoder = UCLDecoder()
    return decoder.decode(s)


def load(fp):
    return loads(fp.read())

if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rb') as f:
        result = load(f)
    print(result)
