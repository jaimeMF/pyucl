from _ucl import ffi, lib as _ucl

if str is bytes:
    str = unicode


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


def _convert_ucl_object_direct(obj):
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


def _convert_ucl_object(obj):
    res = _convert_ucl_object_direct(obj)

    # for https://github.com/vstakhov/libucl/blob/master/README.md#automatic-arrays-creation
    # there doesn't seem to be a function in libucl to do this
    if obj.next != ffi.NULL and obj.type != _ucl.UCL_OBJECT:
        res = [res]
        while obj.next != ffi.NULL:
            obj = obj.next
            res.append(_convert_ucl_object_direct(obj))
    return res


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
        b = s.encode('utf-8')
        _ucl.ucl_parser_add_string(self._parser, b, len(b))
        self._check_error()
        return self._get_result()


def _to_ucl_object(obj):
    if isinstance(obj, list):
        array = _ucl.ucl_object_typed_new(_ucl.UCL_ARRAY)
        for item in obj:
            _ucl.ucl_array_append(array, _to_ucl_object(item))
        return array
    elif isinstance(obj, dict):
        dic = _ucl.ucl_object_typed_new(_ucl.UCL_OBJECT)
        for k, v in obj.items():
            if not isinstance(k, str):
                raise TypeError("UCL only supports string keys: {}".format(k))
            _ucl.ucl_object_replace_key(dic, _to_ucl_object(v), k.encode('utf-8'), 0, True)
        return dic
    elif isinstance(obj, str):
        return _ucl.ucl_object_fromstring(obj.encode('utf-8'))
    elif isinstance(obj, bool):
        return _ucl.ucl_object_frombool(obj)
    elif isinstance(obj, int):
        return _ucl.ucl_object_fromint(obj)
    elif isinstance(obj, float):
        return _ucl.ucl_object_fromdouble(obj)
    elif obj is None:
        return _ucl.ucl_object_typed_new(_ucl.UCL_NULL)
    else:
        raise TypeError("{} is not UCL serializable".format(repr(obj)))

EMITTERS = {
    'config': _ucl.UCL_EMIT_CONFIG,
    'json': _ucl.UCL_EMIT_JSON,
    'json_compact': _ucl.UCL_EMIT_JSON_COMPACT,
    'yaml': _ucl.UCL_EMIT_YAML,
}
DEFAULT_EMITTER = 'config'


class UCLEncoder(object):
    def encode(self, obj, emit_type=DEFAULT_EMITTER):
        emit_type = EMITTERS[emit_type]
        ucl_obj = _to_ucl_object(obj)
        return ffi.string(_ucl.ucl_object_emit(ucl_obj, emit_type)).decode('utf-8')


def loads(s):
    """Load object from a string.

    :param str s: Serialized information in UCL format
    :return: object loaded from the string
    :raises UCLDecoderError: if the string is not valid UCL
    """
    decoder = UCLDecoder()
    return decoder.decode(s)


def load(fp):
    """Load object from the :term:`file object` *fp*.

    See :func:`loads`.
    """
    return loads(fp.read())


def dumps(obj, emit_type=DEFAULT_EMITTER):
    """Serialize *obj* to a :class:`str` with the format specified by *emit_type*.

    :param obj: Object to encode
    :param str emit_type: One of 'config', 'json', 'json_compact' or 'yaml'
    :return: the serialized object
    :rtype: str
    :raises TypeError: if an object can't be converted to a ucl object
    """
    encoder = UCLEncoder()
    return encoder.encode(obj, emit_type)


def dump(obj, fp, emit_type=DEFAULT_EMITTER):
    """Serialize an object to the :term:`file object` *fp*.

    See :func:`dumps`
    """
    s = dumps(obj, emit_type)
    fp.write(s)


if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rt') as f:
        result = load(f)
    dump(result, sys.stdout)
