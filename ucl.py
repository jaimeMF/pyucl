from cffi import FFI

ffi = FFI()

ffi.cdef("""
    typedef enum {
        UCL_OBJECT,
        UCL_ARRAY,
        UCL_INT,
        UCL_FLOAT,
        UCL_STRING,
        UCL_BOOLEAN,
        UCL_TIME,
        UCL_NULL,
        ...
    } ucl_type_t;
    typedef struct {uint16_t type;...;} ucl_object_t;
    typedef struct {...;} ucl_object_iter_t;


    struct ucl_parser* ucl_parser_new (int flags);
    void ucl_parser_free (struct ucl_parser *parser);
    const char *ucl_parser_get_error(struct ucl_parser *parser);
    bool ucl_parser_add_string (struct ucl_parser *parser, const char *data,
        size_t len);
    bool ucl_parser_add_file (struct ucl_parser *parser, const char *filename);
    ucl_object_t* ucl_parser_get_object (struct ucl_parser *parser);

    ucl_object_t * ucl_object_new (void);
    void ucl_object_unref (ucl_object_t *obj);
    const char* ucl_object_key (const ucl_object_t *obj);

    ucl_object_iter_t ucl_object_iterate_new (const ucl_object_t *obj);
    const ucl_object_t* ucl_object_iterate_safe (ucl_object_iter_t iter,
        bool expand_values);
    void ucl_object_iterate_free (ucl_object_iter_t it);

    int64_t ucl_object_toint (const ucl_object_t *obj);
    double ucl_object_todouble (const ucl_object_t *obj);
    const char* ucl_object_tostring (const ucl_object_t *obj);
    const char* ucl_object_tostring_forced (const ucl_object_t *obj);
    bool ucl_object_toboolean (const ucl_object_t *obj);
""")


_ucl = ffi.verify('#include "ucl.h"', libraries=['ucl'])


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
