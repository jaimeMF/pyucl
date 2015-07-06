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
    typedef struct ucl_object_s {uint16_t type; struct ucl_object_s *next; ...;} ucl_object_t;
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


ffi.set_source('_ucl', '#include "ucl.h"', libraries=['ucl'])

if __name__ == "__main__":
    ffi.compile()
