from cffi import FFI

ffi = FFI()

ffi.cdef("""
    typedef enum {
        UCL_OBJECT,
        UCL_STRING,
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
    const ucl_object_t* ucl_iterate_object (const ucl_object_t *obj,
        ucl_object_iter_t *iter, bool expand_values);
    const char* ucl_object_key (const ucl_object_t *obj);

    const char* ucl_object_tostring (const ucl_object_t *obj);
    const char* ucl_object_tostring_forced (const ucl_object_t *obj);
""")


_ucl = ffi.verify('#include "ucl.h"', libraries=['ucl'])


class UclError(Exception):
    pass


class UclDecoderError(UclError):
    pass


class UclConversionError(UclError):
    pass


def _iter_ucl_object(obj):
    iterator = ffi.new('ucl_object_iter_t *')
    cur = ffi.new('ucl_object_t *')
    while True:
        cur = ffi.gc(
            _ucl.ucl_iterate_object(obj, iterator, True),
            _ucl.ucl_object_unref)
        if cur == ffi.NULL:
            break
        yield cur


def _convert_ucl_object(obj):
    if obj.type == _ucl.UCL_OBJECT:
        res = {}
        for child in _iter_ucl_object(obj):
            key = ffi.string(_ucl.ucl_object_key(child)).decode('utf-8')
            value = _convert_ucl_object(child)
            res[key] = value
        return res
    if obj.type == _ucl.UCL_STRING:
        return ffi.string(_ucl.ucl_object_tostring(obj)).decode('utf-8')
    else:
        raise UclConversionError(
            'Unsupported object type: {}'.format(obj.type))


class UclDecoder(object):
    def __init__(self):
        self._parser = ffi.gc(_ucl.ucl_parser_new(0), _ucl.ucl_parser_free)

    def _check_error(self):
        error = _ucl.ucl_parser_get_error(self._parser)
        if error != ffi.NULL:
            raise UclDecoderError(ffi.string(error))

    def _get_result(self):
        obj = _ucl.ucl_parser_get_object(self._parser)
        return _convert_ucl_object(obj)

    def loads(self, s):
        _ucl.ucl_parser_add_string(self._parser, s, len(s))
        self._check_error()
        return self._get_result()

    def load(self, fp):
        contents = fp.read().strip()
        _ucl.ucl_parser_add_string(self._parser, contents, 0)
        self._check_error()
        return self._get_result()

def loads(s):
    decoder = UclDecoder()
    return decoder.loads(s)

def load(fp):
    decoder = UclDecoder()
    return decoder.load(fp)

if __name__ == '__main__':
    import sys
    decoder = UclDecoder()
    with open(sys.argv[1], 'rb') as f:
        result = decoder.load(f)
    print(result)
