/*
 * BSD 3-Clause License
 *
 * Copyright (c) 2017-2018, plures
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


#include <Python.h>
#include "complexobject.h"
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <stdbool.h>
#include "ndtypes.h"
#include "pyndtypes.h"
#include "xnd.h"
#include "util.h"
#include "docstrings.h"

#define XND_MODULE
#include "pyxnd.h"


#ifdef _MSC_VER
  #ifndef UNUSED
    #define UNUSED
  #endif
#else
  #if defined(__GNUC__) && !defined(__INTEL_COMPILER)
    #define UNUSED __attribute__((unused))
  #else
    #define UNUSED
  #endif
#endif


/****************************************************************************/
/*                               Error handling                             */
/****************************************************************************/

static PyObject *
seterr(ndt_context_t *ctx)
{
    return Ndt_SetError(ctx);
}

static int
seterr_int(ndt_context_t *ctx)
{
    (void)Ndt_SetError(ctx);
    return -1;
}

static xnd_t
seterr_xnd(ndt_context_t *ctx)
{
    (void)Ndt_SetError(ctx);
    return xnd_error;
}


/****************************************************************************/
/*                                Singletons                                */
/****************************************************************************/

static PyTypeObject XndEllipsis_Type;

static PyObject XndEllipsisObject = {
    _PyObject_EXTRA_INIT
    .ob_refcnt = 1,
    .ob_type = &XndEllipsis_Type
};

static PyObject *
xnd_ellipsis(void)
{
    Py_INCREF(&XndEllipsisObject);
    return &XndEllipsisObject;
}

static PyObject *
xnd_ellipsis_repr(PyObject *self UNUSED)
{
    return PyUnicode_FromString("...");
}

static PyTypeObject XndEllipsis_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "_xnd.XndEllipsis",
    .tp_repr = xnd_ellipsis_repr
};


/****************************************************************************/
/*                           MemoryBlock Object                             */
/****************************************************************************/

/* This object owns the memory that is shared by several xnd objects. It is
   never exposed to the Python level.

   The memory block is created by the primary xnd object on initialization.
   Sub-views, slices etc. share the memory block.

   PEP-3118 imports are supported.  At a later stage the mblock object will
   potentially need to communicate with Arrow or other formats in order
   to acquire and manage external memory blocks.
*/


typedef struct {
    PyObject_HEAD
    PyObject *type;    /* type owner */
    xnd_master_t *xnd; /* memblock owner */
    Py_buffer *view;   /* PEP-3118 imports */
} MemoryBlockObject;

static int mblock_init(xnd_t * const x, PyObject *v);
static PyTypeObject MemoryBlock_Type;


static MemoryBlockObject *
mblock_alloc(void)
{
    MemoryBlockObject *self;

    self = PyObject_GC_New(MemoryBlockObject, &MemoryBlock_Type);
    if (self == NULL) {
        return NULL;
    }
 
    self->type = NULL;
    self->xnd = NULL;
    self->view = NULL;

    PyObject_GC_Track(self);
    return self;
}

static int
mblock_traverse(MemoryBlockObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->type);
    if (self->view) {
        Py_VISIT(self->view->obj);
    }
    return 0;
}

static void
mblock_dealloc(MemoryBlockObject *self)
{
    PyObject_GC_UnTrack(self);
    xnd_del(self->xnd);
    self->xnd = NULL;
    Py_CLEAR(self->type);
    if (self->view) {
        PyBuffer_Release(self->view);
        ndt_free(self->view);
        self->view = NULL;
    }
    PyObject_GC_Del(self);
}

static MemoryBlockObject *
mblock_empty(PyObject *type)
{
    NDT_STATIC_CONTEXT(ctx);
    MemoryBlockObject *self;

    if (!Ndt_Check(type)) {
        PyErr_SetString(PyExc_TypeError, "expected ndt object");
        return NULL;
    }

    self = mblock_alloc();
    if (self == NULL) {
        return NULL;
    }

    self->xnd = xnd_empty_from_type(CONST_NDT(type), XND_OWN_EMBEDDED, &ctx);
    if (self->xnd == NULL) {
        Py_DECREF(self);
        return (MemoryBlockObject *)seterr(&ctx);
    }
    Py_INCREF(type);
    self->type = type;

    return self;
}

static MemoryBlockObject *
mblock_from_typed_value(PyObject *type, PyObject *value)
{
    MemoryBlockObject *self;

    self = mblock_empty(type);
    if (self == NULL) {
        return NULL;
    }

    if (mblock_init(&self->xnd->master, value) < 0) {
        Py_DECREF(self);
        return NULL;
    }

    return self;
}

static MemoryBlockObject *
mblock_from_xnd(xnd_t *src)
{
    NDT_STATIC_CONTEXT(ctx);
    MemoryBlockObject *self;
    PyObject *type;
    xnd_master_t *x;

    x = xnd_from_xnd(src, XND_OWN_EMBEDDED, &ctx);
    if (x == NULL) {
        return (MemoryBlockObject *)seterr(&ctx);
    }

    type = Ndt_FromType((ndt_t *)x->master.type);
    if (type == NULL) {
        xnd_del(x);
        return NULL;
    }

    self = mblock_alloc();
    if (self == NULL) {
        Py_DECREF(type);
        xnd_del(x);
        return NULL;
    }

    self->type = type;
    self->xnd = x;

    return self;
}

static PyObject *
type_from_buffer(const Py_buffer *view)
{
    NDT_STATIC_CONTEXT(ctx);
    ndt_t *t, *type;
    int64_t shape, step;
    int64_t i;

    if (view->buf == NULL || view->obj == NULL ||
        view->format == NULL || view->suboffsets != NULL) {
        PyErr_SetString(PyExc_BufferError,
            "expect a buffer with full information and no suboffsets");
        return NULL;
    }

    if (view->ndim != 0) {
        if (view->shape == NULL || view->strides == NULL) {
            PyErr_SetString(PyExc_BufferError,
                "expect a buffer with full information");
            return NULL;
        }
    }

    type = ndt_from_bpformat(view->format, &ctx);
    if (type == NULL) {
        return seterr(&ctx);
    }

    if (ndt_itemsize(type) != view->itemsize) {
        PyErr_SetString(PyExc_RuntimeError,
            "mismatch between computed itemsize and buffer itemsize");
        ndt_del(type);
        return NULL;
    }

    for (i=view->ndim-1, t=type; i>=0; i--, type=t) {
        shape = view->shape[i];
        step = view->strides[i] / view->itemsize;
        t = ndt_fixed_dim(type, shape, step, &ctx);
        if (t == NULL) {
            return seterr(&ctx);
        }
    }

    return Ndt_FromType(t);
}

static MemoryBlockObject *
mblock_from_buffer(PyObject *obj)
{
    MemoryBlockObject *self;

    self = mblock_alloc();
    if (self == NULL) {
        return NULL;
    }

    self->view = ndt_calloc(1, sizeof *self->view);
    if (self->view == NULL) {
        Py_DECREF(self);
        return NULL;
    }

    if (PyObject_GetBuffer(obj, self->view, PyBUF_FULL_RO) < 0) {
        Py_DECREF(self);
        return NULL;
    }

    if (!PyBuffer_IsContiguous(self->view, 'A')) {
        /* Conversion from buf+strides to steps+linear_index is not possible
           if the start of the original data is missing. */
        PyErr_SetString(PyExc_NotImplementedError,
            "conversion from non-contiguous buffers is not implemented");
        Py_DECREF(self);
        return NULL;
    }

    self->type = type_from_buffer(self->view);
    if (self->type == NULL) {
        Py_DECREF(self);
        return NULL;
    }

    self->xnd = ndt_calloc(1, sizeof *self->xnd);
    if (self->xnd == NULL) {
        Py_DECREF(self);
        return NULL;
    }

    self->xnd->flags = 0;
    self->xnd->master.bitmap.data = NULL;
    self->xnd->master.bitmap.size = 0;
    self->xnd->master.bitmap.next = NULL;
    self->xnd->master.index = 0;
    self->xnd->master.type = CONST_NDT(self->type);
    self->xnd->master.ptr = self->view->buf;

    return self;
}


static PyTypeObject MemoryBlock_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "_xnd.memblock",
    .tp_basicsize = sizeof(MemoryBlockObject),
    .tp_dealloc = (destructor)mblock_dealloc,
    .tp_hash = PyObject_HashNotImplemented,
    .tp_getattro = PyObject_GenericGetAttr,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .tp_traverse = (traverseproc)mblock_traverse
};


/****************************************************************************/
/*                      MemoryBlock Object Initialization                   */
/****************************************************************************/

#if NDT_SYS_BIG_ENDIAN == 1
  #define XND_REV_COND NDT_LITTLE_ENDIAN
#else
  #define XND_REV_COND NDT_BIG_ENDIAN
#endif

static inline void
memcpy_rev(char *dest, const char *src, size_t size)
{
    size_t i;

    for (i = 0; i < size; i++) {
        dest[i] = src[size-1-i];
    }
}

static inline void
bcopy_swap(char *dest, const char *src, size_t size, uint32_t flags)
{
    if (flags & XND_REV_COND) {
        memcpy_rev(dest, src, size);
    }
    else {
        memcpy(dest, src, size);
    }
}

static inline int
le(uint32_t flags)
{
#if NDT_SYS_BIG_ENDIAN == 1
    return flags & NDT_LITTLE_ENDIAN;
#else
    return !(flags & NDT_BIG_ENDIAN);
#endif
}


#define PACK_SINGLE(ptr, src, type, flags) \
    do {                                                      \
        type _x;                                              \
        _x = (type)src;                                       \
        bcopy_swap(ptr, (const char *)&_x, sizeof _x, flags); \
    } while (0)

#define UNPACK_SINGLE(dest, ptr, type, flags) \
    do {                                                \
        type _x;                                        \
        bcopy_swap((char *)&_x, ptr, sizeof _x, flags); \
        dest = _x;                                      \
    } while (0)


static void
_strncpy(char *dest, const void *src, size_t len, size_t size)
{
    assert (len <= size);
    memcpy(dest, src, len);
    memset(dest+len, '\0', size-len);
}

static int64_t
u8_skip_trailing_zero(const uint8_t *ptr, int64_t codepoints)
{
    int64_t i;

    for (i=codepoints-1; i >= 0; i--)
        if (ptr[i] != 0)
            return i+1;

    return 0;
}

static int64_t
u16_skip_trailing_zero(const uint16_t *ptr, int64_t codepoints)
{
    int64_t i;

    for (i=codepoints-1; i >= 0; i--)
        if (ptr[i] != 0)
            return i+1;

    return 0;
}

static int64_t
u32_skip_trailing_zero(const uint32_t *ptr, int64_t codepoints)
{
    int64_t i;

    for (i=codepoints-1; i >= 0; i--)
        if (ptr[i] != 0)
            return i+1;

    return 0;
}

static int64_t
get_int(PyObject *v, int64_t min, int64_t max)
{
    PyObject *tmp;
    int64_t x;

    tmp = PyNumber_Index(v);
    if (tmp == NULL) {
        return -1;
    }

    x = PyLong_AsLongLong(tmp);
    Py_DECREF(tmp);

    if (x == -1 && PyErr_Occurred()) {
        return -1;
    }

    if (x < min || x > max) {
        PyErr_Format(PyExc_ValueError,
            "out of range: %" PRIi64, x);
        return -1;
    }

    return x;
}

static uint64_t
get_uint(PyObject *v, uint64_t max)
{
    PyObject *tmp;
    unsigned long long x;

    tmp = PyNumber_Index(v);
    if (tmp == NULL) {
        return max;
    }

    x = PyLong_AsUnsignedLongLong(tmp);
    Py_DECREF(tmp);

    if (x == (unsigned long long)-1 && PyErr_Occurred()) {
        return max;
    }

    if (x > max) {
        PyErr_Format(PyExc_ValueError,
            "out of range: %" PRIu64, x);
        return max;
    }

    return x;
}

static int
mblock_init(xnd_t * const x, PyObject *v)
{
    NDT_STATIC_CONTEXT(ctx);
    const ndt_t * const t = x->type;

    if (!check_invariants(t)) {
        return -1;
    }

    if (ndt_is_abstract(t)) {
        PyErr_SetString(PyExc_TypeError, "xnd has abstract type");
        return -1;
    }

    /* Set missing value. */
    if (ndt_is_optional(t)) {
        if (t->ndim > 0) {
            PyErr_SetString(PyExc_NotImplementedError,
                "optional dimensions are not implemented");
            return -1;
        }

        if (v == Py_None) {
            xnd_set_na(x);
            return 0;
        }

        xnd_set_valid(x);
    }

    switch (t->tag) {
    case FixedDim: {
        const int64_t shape = t->FixedDim.shape;
        int64_t i;

        if (!PyList_Check(v)) {
            PyErr_Format(PyExc_TypeError,
                "xnd: expected list, not '%.200s'", Py_TYPE(v)->tp_name);
            return -1;
        }

        if (PyList_GET_SIZE(v) != shape) {
            PyErr_Format(PyExc_ValueError,
                "xnd: expected list with size %" PRIi64, shape);
            return -1;
        }

        for (i = 0; i < shape; i++) {
            xnd_t next = xnd_fixed_dim_next(x, i);
            if (mblock_init(&next, PyList_GET_ITEM(v, i)) < 0) {
                return -1;
            }
        }

        return 0;
    }

    case VarDim: {
        int64_t start, step, shape;
        int64_t i;

        if (!PyList_Check(v)) {
            PyErr_Format(PyExc_TypeError,
                "xnd: expected list, not '%.200s'", Py_TYPE(v)->tp_name);
            return -1;
        }

        shape = ndt_var_indices(&start, &step, t, x->index, &ctx);
        if (shape < 0) {
            return seterr_int(&ctx);
        }

        if (PyList_GET_SIZE(v) != shape) {
            PyErr_Format(PyExc_ValueError,
                "xnd: expected list with size %" PRIi64, shape);
            return -1;
        }

        for (i = 0; i < shape; i++) {
            xnd_t next = xnd_var_dim_next(x, start, step, i);
            if (mblock_init(&next, PyList_GET_ITEM(v, i)) < 0) {
                return -1;
            }
        }

        return 0;
    }

    case Tuple: {
        const int64_t shape = t->Tuple.shape;
        int64_t i;

        if (!PyTuple_Check(v)) {
            PyErr_Format(PyExc_TypeError,
                "xnd: expected tuple, not '%.200s'", Py_TYPE(v)->tp_name);
            return -1;
        }

        if (PyTuple_GET_SIZE(v) != shape) {
            PyErr_Format(PyExc_ValueError,
                "xnd: expected tuple with size %" PRIi64, shape);
            return -1;
        }

        for (i = 0; i < shape; i++) {
            xnd_t next = xnd_tuple_next(x, i, &ctx);
            if (next.ptr == NULL) {
                return seterr_int(&ctx);
            }

            if (mblock_init(&next, PyTuple_GET_ITEM(v, i)) < 0) {
                return -1;
            }
        }

        return 0;
    }

    case Record: {
        const int64_t shape = t->Record.shape;
        PyObject *tmp;
        int64_t i;
        int ret;

        if (!PyDict_Check(v)) {
            PyErr_Format(PyExc_TypeError,
                "xnd: expected dict, not '%.200s'", Py_TYPE(v)->tp_name);
            return -1;
        }

        if (PyDict_Size(v) != shape) {
            PyErr_Format(PyExc_ValueError,
                "xnd: expected dict with size %" PRIi64, shape);
            return -1;
        }

        for (i = 0; i < shape; i++) {
            xnd_t next = xnd_record_next(x, i, &ctx);
            if (next.ptr == NULL) {
                return seterr_int(&ctx);
            }

            tmp = PyMapping_GetItemString(v, t->Record.names[i]);
            if (tmp == NULL) {
                if (!PyErr_Occurred()) {
                    PyErr_Format(PyExc_ValueError,
                        "xnd: key not found %s", t->Record.names[i]);
                }
                return -1;
            }

            ret = mblock_init(&next, tmp);
            Py_DECREF(tmp);
            if (ret < 0) {
                return -1;
            }
        }

        return 0;
    }

    case Ref: {
        xnd_t next = xnd_ref_next(x, &ctx);
        if (next.ptr == NULL) {
            return seterr_int(&ctx);
        }

        return mblock_init(&next, v);
    }

    case Constr: {
        xnd_t next = xnd_constr_next(x, &ctx);
        if (next.ptr == NULL) {
            return seterr_int(&ctx);
        }

        return mblock_init(&next, v);
    }

    case Nominal: {
        xnd_t next = xnd_nominal_next(x, &ctx);
        if (next.ptr == NULL) {
            return seterr_int(&ctx);
        }

        if (t->Nominal.meth->init != NULL) {
            if (!t->Nominal.meth->init(&next, v, &ctx)) {
                return -1;
            }
            return 0;
        }

        int ret = mblock_init(&next, v);
        if (ret < 0) {
            return ret;
        }

        if (t->Nominal.meth->constraint != NULL &&
            !t->Nominal.meth->constraint(&next, &ctx)) {
            return seterr_int(&ctx);
        }

        return ret;
    }

    case Bool: {
        int tmp;
        bool b;

        if (v == Py_None) {
            PyErr_SetString(PyExc_ValueError,
                "assigning None to memory block with non-optional type");
            return -1;
        }

        tmp = PyObject_IsTrue(v);
        if (tmp < 0) {
            return -1;
        }
        b = (bool)tmp;

        PACK_SINGLE(x->ptr, b, bool, t->flags);
        return 0;
    }

    case Int8: {
        int8_t tmp = (int8_t)get_int(v, INT8_MIN, INT8_MAX);
        if (tmp == -1 && PyErr_Occurred()) {
            return -1;
        }
        PACK_SINGLE(x->ptr, tmp, int8_t, t->flags);
        return 0;
    }

    case Int16: {
        int16_t tmp = (int16_t)get_int(v, INT16_MIN, INT16_MAX);
        if (tmp == -1 && PyErr_Occurred()) {
            return -1;
        }
        PACK_SINGLE(x->ptr, tmp, int16_t, t->flags);
        return 0;
    }

    case Int32: {
        int32_t tmp = (int32_t)get_int(v, INT32_MIN, INT32_MAX);
        if (tmp == -1 && PyErr_Occurred()) {
            return -1;
        }
        PACK_SINGLE(x->ptr, tmp, int32_t, t->flags);
        return 0;
    }

    case Int64: {
        int64_t tmp = get_int(v, INT64_MIN, INT64_MAX);
        if (tmp == -1 && PyErr_Occurred()) {
            return -1;
        }
        PACK_SINGLE(x->ptr, tmp, int64_t, t->flags);
        return 0;
    }

    case Uint8: {
        uint8_t tmp = (uint8_t)get_uint(v, UINT8_MAX);
        if (tmp == UINT8_MAX && PyErr_Occurred()) {
            return -1;
        }
        PACK_SINGLE(x->ptr, tmp, uint8_t, t->flags);
        return 0;
    }

    case Uint16: {
        uint16_t tmp = (uint16_t)get_uint(v, UINT16_MAX);
        if (tmp == UINT16_MAX && PyErr_Occurred()) {
            return -1;
        }
        PACK_SINGLE(x->ptr, tmp, uint16_t, t->flags);
        return 0;
    }

    case Uint32: {
        uint32_t tmp = (uint32_t)get_uint(v, UINT32_MAX);
        if (tmp == UINT32_MAX && PyErr_Occurred()) {
            return -1;
        }
        PACK_SINGLE(x->ptr, tmp, uint32_t, t->flags);
        return 0;
    }

    case Uint64: {
        uint64_t tmp = get_uint(v, UINT64_MAX);
        if (tmp == UINT64_MAX && PyErr_Occurred()) {
            return -1;
        }
        PACK_SINGLE(x->ptr, tmp, uint64_t, t->flags);
        return 0;
    }

    case Float16: {
#if PY_VERSION_HEX >= 0x03060000
        double tmp = PyFloat_AsDouble(v);
        if (tmp == -1 && PyErr_Occurred()) {
            return -1;
        }
        return _PyFloat_Pack2(tmp, (unsigned char *)x->ptr, le(t->flags));
#else
        PyErr_SetString(PyExc_NotImplementedError,
            "half-float not implemented in Python versions < 3.6");
        return -1;
#endif
    }

    case Float32: {
        double tmp = PyFloat_AsDouble(v);
        if (tmp == -1 && PyErr_Occurred()) {
            return -1;
        }
        return _PyFloat_Pack4(tmp, (unsigned char *)x->ptr, le(t->flags));
    }

    case Float64: {
        double tmp = PyFloat_AsDouble(v);
        if (tmp == -1 && PyErr_Occurred()) {
            return -1;
        }
        return _PyFloat_Pack8(tmp, (unsigned char *)x->ptr, le(t->flags));
    }

    case Complex32: {
#if PY_VERSION_HEX >= 0x03060000
        Py_complex c = PyComplex_AsCComplex(v);
        if (c.real == -1.0 && PyErr_Occurred()) {
            return -1;
        }
        if (_PyFloat_Pack2(c.real, (unsigned char *)x->ptr, le(t->flags)) < 0) {
            return -1;
        }
        return _PyFloat_Pack2(c.imag, (unsigned char *)(x->ptr+2), le(t->flags));
#else
        PyErr_SetString(PyExc_NotImplementedError,
            "half-float not implemented in Python versions < 3.6");
        return -1;
#endif
    }

    case Complex64: {
        Py_complex c = PyComplex_AsCComplex(v);
        if (c.real == -1.0 && PyErr_Occurred()) {
            return -1;
        }
        if (_PyFloat_Pack4(c.real, (unsigned char *)x->ptr, le(t->flags)) < 0) {
            return -1;
        }
        return _PyFloat_Pack4(c.imag, (unsigned char *)(x->ptr+4), le(t->flags));
    }

    case Complex128: {
        Py_complex c = PyComplex_AsCComplex(v);
        if (c.real == -1.0 && PyErr_Occurred()) {
            return -1;
        }
        if (_PyFloat_Pack8(c.real, (unsigned char *)x->ptr, le(t->flags)) < 0) {
            return -1;
        }
        return _PyFloat_Pack8(c.imag, (unsigned char *)(x->ptr+8), le(t->flags));
    }

    case FixedString: {
        int64_t codepoints = t->FixedString.size;
        int64_t len;

        if (!PyUnicode_Check(v)) {
            PyErr_SetString(PyExc_TypeError, "expected unicode object");
            return -1;
        }

        if (PyUnicode_READY(v) < 0) {
            return -1;
        }

        switch (t->FixedString.encoding) {
        case Ascii: {
            if (!PyUnicode_IS_ASCII(v)) {
                PyErr_SetString(PyExc_ValueError,
                    "expected ascii string");
                return -1;
            }

            len = PyUnicode_GET_LENGTH(v);

            if (len > t->datasize) {
                PyErr_Format(PyExc_ValueError,
                    "maximum string size (in bytes) is %" PRIi64, codepoints);
                return -1;
            }

            _strncpy(x->ptr, PyUnicode_1BYTE_DATA(v), (size_t)len, (size_t)t->datasize);
            return 0;
        }

        case Utf8: {
            if (PyUnicode_KIND(v) != PyUnicode_1BYTE_KIND) {
                PyErr_SetString(PyExc_ValueError,
                    "expected utf8 string");
                return -1;
            }

            len = PyUnicode_GET_LENGTH(v);
            if (len > t->datasize) {
                PyErr_Format(PyExc_ValueError,
                    "maximum string size (in UTF-8 code points) is %" PRIi64, codepoints);
                return -1;
            }

            _strncpy(x->ptr, PyUnicode_1BYTE_DATA(v), (size_t)len, (size_t)t->datasize);
            return 0;
        }

        case Utf16: {
            PyObject *b = PyUnicode_AsUTF16String(v);
            if (b == NULL) {
                return -1;
            }

            len = PyBytes_GET_SIZE(b);

            if (len-2 > t->datasize) {
                PyErr_Format(PyExc_ValueError,
                    "maximum string size (in UTF-16 code points) is %" PRIi64, codepoints);
                return -1;
            }

            /* skip byte order mark */
            assert(len >= 2);

            _strncpy(x->ptr, PyBytes_AS_STRING(b)+2, (size_t)(len-2), (size_t)t->datasize);
            Py_DECREF(b);

            return 0;
        }

        case Utf32: {
            PyObject *b = PyUnicode_AsUTF32String(v);
            if (b == NULL) {
                return -1;
            }

            len = PyBytes_GET_SIZE(b);

            if (len-4 > t->datasize) {
                PyErr_Format(PyExc_ValueError,
                    "maximum string size (in UTF-32 code points) is %" PRIi64, codepoints);
                return -1;
            }

            /* skip byte order mark */
            assert(len >= 4);

            _strncpy(x->ptr, PyBytes_AS_STRING(b)+4, (size_t)(len-4), (size_t)t->datasize);
            Py_DECREF(b);

            return 0;
        }

        case Ucs2:
            PyErr_SetString(PyExc_NotImplementedError,
                "ucs2 encoding not implemented");
            return -1;

        default:
            PyErr_SetString(PyExc_RuntimeError, "invalid encoding");
            return -1;
        }
    }

    case FixedBytes: {
        int64_t size = t->FixedBytes.size;
        int64_t len;

        if (!PyBytes_Check(v)) {
            PyErr_SetString(PyExc_TypeError, "expected bytes object");
            return -1;
        }

        len = PyBytes_GET_SIZE(v);

        if (len > size) {
            PyErr_Format(PyExc_ValueError,
                "maximum bytes size is %" PRIi64, size);
            return -1;
        }

        _strncpy(x->ptr, PyBytes_AS_STRING(v), (size_t)len, (size_t)size);

        return 0;
    }

    case String: {
        Py_ssize_t size;
        const char *cp;
        char *s;

        cp = PyUnicode_AsUTF8AndSize(v, &size);
        if (cp == NULL) {
            return -1;
        }

        s = ndt_strdup(cp, &ctx);
        if (s == NULL) {
            return seterr_int(&ctx);
        }

        if (XND_POINTER_DATA(x->ptr)) {
            ndt_free(XND_POINTER_DATA(x->ptr));
        }

        XND_POINTER_DATA(x->ptr) = s;
        return 0;
    }

    case Bytes: {
        Py_ssize_t size;
        char *cp;
        char *s;

        if (PyBytes_AsStringAndSize(v, &cp, &size) < 0) {
            return -1;
        }

        s = ndt_aligned_calloc(t->Bytes.target_align, size);
        if (s == NULL) {
            PyErr_NoMemory();
            return -1;
        }

        memcpy(s, cp, size);

        if (XND_BYTES_DATA(x->ptr)) {
            ndt_aligned_free(XND_BYTES_DATA(x->ptr));
        }

        XND_BYTES_SIZE(x->ptr) = size;
        XND_BYTES_DATA(x->ptr) = (uint8_t *)s;
        return 0;
    }

    case Categorical: {
        int64_t k;

        if (PyBool_Check(v)) {
            int tmp = PyObject_IsTrue(v);
            if (tmp < 0) {
                return -1;
            }

            for (k = 0; k < t->Categorical.ntypes; k++) {
                if (t->Categorical.types[k].tag == ValBool &&
                    tmp == t->Categorical.types[k].ValBool) {
                    PACK_SINGLE(x->ptr, k, int64_t, t->flags);
                    return 0;
                }
            }
            goto not_found;
        }

        else if (PyLong_Check(v)) {
            int64_t tmp = get_int(v, INT64_MIN, INT64_MAX);
            if (tmp == -1 && PyErr_Occurred()) {
                return -1;
            }

            for (k = 0; k < t->Categorical.ntypes; k++) {
                if (t->Categorical.types[k].tag == ValInt64 &&
                    tmp == t->Categorical.types[k].ValInt64) {
                    PACK_SINGLE(x->ptr, k, int64_t, t->flags);
                    return 0;
                }
            }
            goto not_found;
        }

        else if (PyFloat_Check(v)) {
            double tmp = PyFloat_AsDouble(v);
            if (tmp == -1 && PyErr_Occurred()) {
                return -1;
            }

            for (k = 0; k < t->Categorical.ntypes; k++) {
                /* XXX: DBL_EPSILON? */
                if (t->Categorical.types[k].tag == ValFloat64 &&
                    tmp == t->Categorical.types[k].ValFloat64) {
                    PACK_SINGLE(x->ptr, k, int64_t, t->flags);
                    return 0;
                }
            }
            goto not_found;
        }

        else if (PyUnicode_Check(v)) {
            const char *tmp = PyUnicode_AsUTF8(v);
            if (tmp == NULL) {
                return -1;
            }

            for (k = 0; k < t->Categorical.ntypes; k++) {
                if (t->Categorical.types[k].tag == ValString &&
                    strcmp(tmp, t->Categorical.types[k].ValString) == 0) {
                    PACK_SINGLE(x->ptr, k, int64_t, t->flags);
                    return 0;
                }
            }
            goto not_found;
        }

    not_found:
        for (k = 0; k < t->Categorical.ntypes; k++) {
            if (t->Categorical.types[k].tag == ValNA) {
                PACK_SINGLE(x->ptr, k, int64_t, t->flags);
                return 0;
            }
        }

        PyErr_Format(PyExc_ValueError, "category not found for: %.200R", v);
        return -1;
    }

    case Char:
        PyErr_SetString(PyExc_NotImplementedError,
            "'Char' type semantics need to be defined");
        return -1;

    case Module:
        PyErr_SetString(PyExc_NotImplementedError,
            "'Module' type not implemented");
        return -1;

    /* NOT REACHED: intercepted by ndt_is_abstract(). */
    case AnyKind: case SymbolicDim: case EllipsisDim: case Typevar:
    case ScalarKind: case SignedKind: case UnsignedKind: case FloatKind:
    case ComplexKind: case FixedStringKind: case FixedBytesKind:
    case Function:
        PyErr_SetString(PyExc_RuntimeError, "unexpected abstract type");
        return -1;
    }

    /* NOT REACHED: tags should be exhaustive */
    PyErr_SetString(PyExc_RuntimeError, "invalid type tag");
    return -1;
}


/****************************************************************************/
/*                                 xnd object                               */
/****************************************************************************/

typedef struct {
    PyObject_HEAD
    MemoryBlockObject *mblock; /* owner of the primary type and memory block */
    PyObject *type;            /* owner of the current type */
    xnd_t xnd;                 /* typed view, does not own anything */
} XndObject;

static PyTypeObject Xnd_Type;

#define TYPE_OWNER(v) (((XndObject *)v)->type)
#define XND(v) (&(((XndObject *)v)->xnd))
#define XND_INDEX(v) (((XndObject *)v)->xnd.index)
#define XND_TYPE(v) (((XndObject *)v)->xnd.type)
#define XND_PTR(v) (((XndObject *)v)->xnd.ptr)


static inline bool
is_readonly(XndObject *self)
{
    return self->mblock->view != NULL && self->mblock->view->readonly;
}


static XndObject *
pyxnd_alloc(PyTypeObject *type)
{
    XndObject *self;

    self = (XndObject *)type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }
 
    self->mblock = NULL;
    self->type = NULL;
    self->xnd.bitmap.data = NULL;
    self->xnd.bitmap.size = 0;
    self->xnd.bitmap.next = NULL;
    self->xnd.index = 0;
    self->xnd.type  = NULL;
    self->xnd.ptr = NULL;

    return self;
}

static int
pyxnd_traverse(XndObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->mblock);
    Py_VISIT(self->type);
    return 0;
}

static void
pyxnd_dealloc(XndObject *self)
{
    PyObject_GC_UnTrack(self);
    Py_CLEAR(self->mblock);
    Py_CLEAR(self->type);
    Py_TYPE(self)->tp_free(self);
}

static PyObject *
pyxnd_from_mblock(PyTypeObject *tp, MemoryBlockObject *mblock)
{
    XndObject *self;

    self = pyxnd_alloc(tp);
    if (self == NULL) {
        Py_DECREF(mblock);
        return NULL;
    }

    Py_INCREF(mblock->type);
    self->mblock = mblock;
    self->type = mblock->type;
    self->xnd = mblock->xnd->master;

    return (PyObject *)self;
}

static PyObject *
pyxnd_new(PyTypeObject *tp, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"type", "value", NULL};
    PyObject *type = NULL;
    PyObject *value = NULL;
    MemoryBlockObject *mblock;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist, &type,
        &value)) {
        return NULL;
    }

    mblock = mblock_from_typed_value(type, value);
    if (mblock == NULL) {
        return NULL;
    }

    return pyxnd_from_mblock(tp, mblock);
}

static PyObject *
pyxnd_empty(PyTypeObject *tp, PyObject *type)
{
    MemoryBlockObject *mblock;

    type = Ndt_FromObject(type);
    if (type == NULL) {
        return NULL;
    }

    mblock = mblock_empty(type);
    Py_DECREF(type);
    if (mblock == NULL) {
        return NULL;
    }

    return pyxnd_from_mblock(tp, mblock);
}

static PyObject *
pyxnd_from_buffer(PyTypeObject *tp, PyObject *obj)
{
    MemoryBlockObject *mblock;

    mblock = mblock_from_buffer(obj);
    if (mblock == NULL) {
        return NULL;
    }

    return pyxnd_from_mblock(tp, mblock);
}


/******************************************************************************/
/*                                 xnd methods                                */
/******************************************************************************/

static int
dict_set_item(PyObject *dict, const char *k, PyObject *value)
{
    PyObject *key;
    int ret;

    key = PyUnicode_FromString(k);
    if (key == NULL) {
        return -1;
    }

    ret = PyDict_SetItem(dict, key, value);
    Py_DECREF(key);

    return ret;
}

static PyObject *
_pyxnd_value(const xnd_t * const x, const int64_t maxshape)
{
    NDT_STATIC_CONTEXT(ctx);
    const ndt_t * const t = x->type;

    assert(ndt_is_concrete(t));

    /* Bitmap access needs the linear index. */
    if (xnd_is_na(x)) {
        Py_RETURN_NONE;
    }

    switch (t->tag) {
    case FixedDim: {
        PyObject *lst, *v;
        int64_t shape, i;

        shape = t->FixedDim.shape;
        if (shape > maxshape) {
            shape = maxshape;
        }

        lst = list_new(shape);
        if (lst == NULL) {
            return NULL;
        }

        for (i = 0; i < shape; i++) {
            if (i == maxshape-1) {
                PyList_SET_ITEM(lst, i, xnd_ellipsis());
                break;
            }

            const xnd_t next = xnd_fixed_dim_next(x, i);
            v = _pyxnd_value(&next, maxshape);
            if (v == NULL) {
                Py_DECREF(lst);
                return NULL;
            }
            PyList_SET_ITEM(lst, i, v);
        }

        return lst;
    }

    case VarDim: {
        PyObject *lst, *v;
        int64_t start, step, shape;
        int64_t i;

        shape = ndt_var_indices(&start, &step, t, x->index, &ctx);
        if (shape < 0) {
            return seterr(&ctx);
        }
        if (shape > maxshape) {
            shape = maxshape;
        }

        lst = list_new(shape);
        if (lst == NULL) {
            return NULL;
        }

        for (i = 0; i < shape; i++) {
            if (i == maxshape-1) {
                PyList_SET_ITEM(lst, i, xnd_ellipsis());
                break;
            }

            const xnd_t next = xnd_var_dim_next(x, start, step, i);
            v = _pyxnd_value(&next, maxshape);
            if (v == NULL) {
                Py_DECREF(lst);
                return NULL;
            }
            PyList_SET_ITEM(lst, i, v);
        }

        return lst;
    }

    case Tuple: {
        PyObject *tuple, *v;
        int64_t shape, i;

        shape = t->Tuple.shape;
        if (shape > maxshape) {
            shape = maxshape;
        }

        tuple = tuple_new(shape);
        if (tuple == NULL) {
            return NULL;
        }

        for (i = 0; i < shape; i++) {
            if (i == maxshape-1) {
                PyTuple_SET_ITEM(tuple, i, xnd_ellipsis());
                break;
            }

            const xnd_t next = xnd_tuple_next(x, i, &ctx);
            if (next.ptr == NULL) {
                return seterr(&ctx);
            }

            v = _pyxnd_value(&next, maxshape);
            if (v == NULL) {
                Py_DECREF(tuple);
                return NULL;
            }
            PyTuple_SET_ITEM(tuple, i, v);
        }

        return tuple;
    }

    case Record: {
        PyObject *dict, *v;
        int64_t shape, i;
        int ret;

        shape = t->Record.shape;
        if (shape > maxshape) {
            shape = maxshape;
        }

        dict = PyDict_New();
        if (dict == NULL) {
            return NULL;
        }

        for (i = 0; i < shape; i++) {
            if (i == maxshape-1) {
                ret = PyDict_SetItem(dict, &XndEllipsisObject, &XndEllipsisObject);
                if (ret < 0) {
                    Py_DECREF(dict);
                    return NULL;
                }
                break;
            }

            const xnd_t next = xnd_record_next(x, i, &ctx);
            if (next.ptr == NULL) {
                return seterr(&ctx);
            }

            v = _pyxnd_value(&next, maxshape);
            if (v == NULL) {
                Py_DECREF(dict);
                return NULL;
            }

            ret = dict_set_item(dict, t->Record.names[i], v);
            Py_DECREF(v);
            if (ret < 0) {
                Py_DECREF(dict);
                return NULL;
            }
        }

        return dict;
    }

    case Ref: {
        const xnd_t next = xnd_ref_next(x, &ctx);
        if (next.ptr == NULL) {
            return seterr(&ctx);
        }

        return _pyxnd_value(&next, maxshape);
    }

    case Constr: {
        const xnd_t next = xnd_constr_next(x, &ctx);
        if (next.ptr == NULL) {
            return seterr(&ctx);
        }

        return _pyxnd_value(&next, maxshape);
    }

    case Nominal: {
        const xnd_t next = xnd_nominal_next(x, &ctx);
        if (next.ptr == NULL) {
            return seterr(&ctx);
        }

        if (t->Nominal.meth->repr != NULL) {
            return t->Nominal.meth->repr(&next, &ctx);
        }

        return _pyxnd_value(&next, maxshape);
    }

    case Bool: {
        bool tmp;
        UNPACK_SINGLE(tmp, x->ptr, bool, t->flags);
        return PyBool_FromLong(tmp);
    }

    case Int8: {
        int8_t tmp;
        UNPACK_SINGLE(tmp, x->ptr, int8_t, t->flags);
        return PyLong_FromLong(tmp);
    }

    case Int16: {
        int16_t tmp;
        UNPACK_SINGLE(tmp, x->ptr, int16_t, t->flags);
        return PyLong_FromLong(tmp);
    }

    case Int32: {
        int32_t tmp;
        UNPACK_SINGLE(tmp, x->ptr, int32_t, t->flags);
        return PyLong_FromLong(tmp);
    }

    case Int64: {
        int64_t tmp;
        UNPACK_SINGLE(tmp, x->ptr, int64_t, t->flags);
        return PyLong_FromLongLong(tmp);
    }

    case Uint8: {
        uint8_t tmp;
        UNPACK_SINGLE(tmp, x->ptr, uint8_t, t->flags);
        return PyLong_FromUnsignedLong(tmp);
    }

    case Uint16: {
        uint16_t tmp;
        UNPACK_SINGLE(tmp, x->ptr, uint16_t, t->flags);
        return PyLong_FromUnsignedLong(tmp);
    }

    case Uint32: {
        uint32_t tmp;
        UNPACK_SINGLE(tmp, x->ptr, uint32_t, t->flags);
        return PyLong_FromUnsignedLong(tmp);
    }

    case Uint64: {
        uint64_t tmp;
        UNPACK_SINGLE(tmp, x->ptr, uint64_t, t->flags);
        return PyLong_FromUnsignedLongLong(tmp);
    }

    case Float16: {
#if PY_VERSION_HEX >= 0x03060000
        double tmp = _PyFloat_Unpack2((unsigned char *)x->ptr, le(t->flags));
        if (tmp == -1.0 && PyErr_Occurred()) {
            return NULL;
        }
        return PyFloat_FromDouble(tmp);
#else
        PyErr_SetString(PyExc_NotImplementedError,
            "half-float not implemented in Python versions < 3.6");
        return NULL;
#endif
    }

    case Float32: {
        double tmp = _PyFloat_Unpack4((unsigned char *)x->ptr, le(t->flags));
        if (tmp == -1.0 && PyErr_Occurred()) {
            return NULL;
        }
        return PyFloat_FromDouble(tmp);
    }

    case Float64: {
        double tmp = _PyFloat_Unpack8((unsigned char *)x->ptr, le(t->flags));
        if (tmp == -1.0 && PyErr_Occurred()) {
            return NULL;
        }
        return PyFloat_FromDouble(tmp);
    }

    case Complex32: {
#if PY_VERSION_HEX >= 0x03060000
        Py_complex c;
        c.real = _PyFloat_Unpack2((unsigned char *)x->ptr, le(t->flags));
        if (c.real == -1.0 && PyErr_Occurred()) {
            return NULL;
        }
        c.imag = _PyFloat_Unpack2((unsigned char *)x->ptr+2, le(t->flags));
        if (c.imag == -1.0 && PyErr_Occurred()) {
            return NULL;
        }
        return PyComplex_FromCComplex(c);
#else
        PyErr_SetString(PyExc_NotImplementedError,
            "half-float not implemented in Python versions < 3.6");
        return NULL;
#endif
    }

    case Complex64: {
        Py_complex c;
        c.real = _PyFloat_Unpack4((unsigned char *)x->ptr, le(t->flags));
        if (c.real == -1.0 && PyErr_Occurred()) {
            return NULL;
        }
        c.imag = _PyFloat_Unpack4((unsigned char *)x->ptr+4, le(t->flags));
        if (c.imag == -1.0 && PyErr_Occurred()) {
            return NULL;
        }
        return PyComplex_FromCComplex(c);
    }

    case Complex128: {
        Py_complex c;
        c.real = _PyFloat_Unpack8((unsigned char *)x->ptr, le(t->flags));
        if (c.real == -1.0 && PyErr_Occurred()) {
            return NULL;
        }
        c.imag = _PyFloat_Unpack8((unsigned char *)x->ptr+8, le(t->flags));
        if (c.imag == -1.0 && PyErr_Occurred()) {
            return NULL;
        }
        return PyComplex_FromCComplex(c);
    }

    case FixedString: {
        int64_t codepoints = t->FixedString.size;

        switch (t->FixedString.encoding) {
        case Ascii:
            codepoints = u8_skip_trailing_zero((uint8_t *)x->ptr, codepoints);
            return unicode_from_kind_and_data(PyUnicode_1BYTE_KIND, x->ptr, codepoints);

        case Utf8:
            codepoints = u8_skip_trailing_zero((uint8_t *)x->ptr, codepoints);
            return unicode_from_kind_and_data(PyUnicode_1BYTE_KIND, x->ptr, codepoints);

        case Utf16:
            codepoints = u16_skip_trailing_zero((uint16_t *)x->ptr, codepoints);
            return unicode_from_kind_and_data(PyUnicode_2BYTE_KIND, x->ptr, codepoints);

        case Utf32:
            codepoints = u32_skip_trailing_zero((uint32_t *)x->ptr, codepoints);
            return unicode_from_kind_and_data(PyUnicode_4BYTE_KIND, x->ptr, codepoints);

        case Ucs2:
            PyErr_SetString(PyExc_NotImplementedError,
                "ucs2 encoding not implemented");
            return NULL;

        default:
            PyErr_SetString(PyExc_RuntimeError, "invalid encoding");
            return NULL;
        }
    }

    case FixedBytes: {
        return bytes_from_string_and_size(x->ptr, t->FixedBytes.size);
    }

    case String: {
        const char *s = XND_POINTER_DATA(x->ptr);
        Py_ssize_t size = s ? strlen(s) : 0;

        return PyUnicode_FromStringAndSize(s, size);
    }

    case Bytes: {
        char *s = (char *)XND_BYTES_DATA(x->ptr);
        int64_t size = XND_BYTES_SIZE(x->ptr);

        return bytes_from_string_and_size(s, size);
    }

    case Categorical: {
        int64_t k;

        UNPACK_SINGLE(k, x->ptr, int64_t, t->flags);

        switch (t->Categorical.types[k].tag) {
        case ValBool: {
            bool tmp = t->Categorical.types[k].ValBool;
            return PyBool_FromLong(tmp);
        }

        case ValInt64: {
            int64_t tmp = t->Categorical.types[k].ValInt64;
            return PyLong_FromLongLong(tmp);
        }

        case ValFloat64: {
            double tmp = t->Categorical.types[k].ValFloat64;
            return PyFloat_FromDouble(tmp);
        }

        case ValString: {
            const char *tmp = t->Categorical.types[k].ValString;
            return PyUnicode_FromString(tmp);
        }

        case ValNA: {
            Py_RETURN_NONE;
        }

        }

        PyErr_SetString(PyExc_RuntimeError, "unexpected category tag");
        return NULL;
    }

    case Char:
        PyErr_SetString(PyExc_NotImplementedError,
            "'Char' type semantics need to be defined");
        return NULL;

    case Module:
        PyErr_SetString(PyExc_NotImplementedError,
            "'Module' type not implemented");
        return NULL;

    /* NOT REACHED: intercepted by ndt_is_abstract(). */
    case AnyKind: case SymbolicDim: case EllipsisDim: case Typevar:
    case ScalarKind: case SignedKind: case UnsignedKind: case FloatKind:
    case ComplexKind: case FixedStringKind: case FixedBytesKind:
    case Function:
        PyErr_SetString(PyExc_RuntimeError, "unexpected abstract type");
        return NULL;
    }

    /* NOT REACHED: tags should be exhaustive */
    PyErr_SetString(PyExc_RuntimeError, "invalid type tag");
    return NULL;
}


/******************************************************************************/
/*                            Indexing and slicing                            */
/******************************************************************************/

static PyObject *
pyxnd_view_copy_type(const XndObject *src, const xnd_t *x)
{
    XndObject *view;
    PyObject *type;

    type = Ndt_CopySubtree(src->type, x->type);
    if (type == NULL) {
        return NULL;
    }

    view = pyxnd_alloc(Py_TYPE(src));
    if (view == NULL) {
        Py_DECREF(type);
        return NULL;
    }

    Py_INCREF(src->mblock);
    view->mblock = src->mblock;
    view->type = type;
    view->xnd = *x;
    view->xnd.type = CONST_NDT(type);

    return (PyObject *)view;
}

static PyObject *
pyxnd_view_move_type(const XndObject *src, xnd_t *x)
{
    XndObject *view;
    PyObject *type;

    type = Ndt_MoveSubtree(src->type, (ndt_t *)x->type);
    if (type == NULL) {
        return NULL;
    }

    view = pyxnd_alloc(Py_TYPE(src));
    if (view == NULL) {
        Py_DECREF(type);
        return NULL;
    }

    Py_INCREF(src->mblock);
    view->mblock = src->mblock;
    view->type = type;
    view->xnd = *x;

    return (PyObject *)view;
}

static Py_ssize_t
pyxnd_len(const xnd_t *x)
{
    NDT_STATIC_CONTEXT(ctx);
    const ndt_t *t = x->type;

    assert(ndt_is_concrete(t));

    if (t->ndim > 0 && ndt_is_optional(t)) {
        PyErr_SetString(PyExc_NotImplementedError,
            "optional dimensions are not supported");
        return -1;
    }

    if (xnd_is_na(x)) {
        return 0;
    }

    switch (t->tag) {
    case FixedDim: {
        return safe_downcast(t->FixedDim.shape);
    }

    case VarDim: {
        int64_t start, step, shape;

        shape = ndt_var_indices(&start, &step, t, x->index, &ctx);
        if (shape < 0) {
            return seterr_int(&ctx);
        }

        return safe_downcast(shape);
    }

    case Tuple: {
        return safe_downcast(t->Tuple.shape);
    }

    case Record: {
        return safe_downcast(t->Record.shape);
    }

    case Ref: {
        const xnd_t next = xnd_ref_next(x, &ctx);
        if (next.ptr == NULL) {
            return seterr_int(&ctx);
        }

        return pyxnd_len(&next);
    }

    case Constr: {
        const xnd_t next = xnd_constr_next(x, &ctx);
        if (next.ptr == NULL) {
            return seterr_int(&ctx);
        }

        return pyxnd_len(&next);
    }

    case Nominal: {
        const xnd_t next = xnd_nominal_next(x, &ctx);
        if (next.ptr == NULL) {
            return seterr_int(&ctx);
        }

        return pyxnd_len(&next);
    }

    default:
        PyErr_SetString(PyExc_TypeError, "type has no len()");
        return -1;
    }
}

static Py_ssize_t
pyxnd_length(XndObject *self)
{
    return pyxnd_len(XND(self));
}

static int64_t
get_index(PyObject *key, int64_t shape)
{
    int64_t i = PyNumber_AsSsize_t(key, PyExc_IndexError);
    if (i == -1 && PyErr_Occurred()) {
        return -1;
    }

    if (i < 0) {
        i += shape;
    }

    if (i < 0 || i >= shape || i > PY_SSIZE_T_MAX) {
        PyErr_SetString(PyExc_IndexError, "index out of bounds");
        return -1;
    }

    return i;
}

static int64_t
get_index_record(const ndt_t *t, PyObject *key)
{
    assert(t->tag == Record);

    if (PyUnicode_Check(key)) {
        int64_t i;

        for (i = 0; i < t->Record.shape; i++) {
            if (PyUnicode_CompareWithASCIIString(
                    key, t->Record.names[i]) == 0) {
                return i;
            }
        }

        PyErr_SetString(PyExc_KeyError, "key not found");
        return -1;
    }

    return get_index(key, t->Record.shape);
}

static void
set_index_exception(bool indexable)
{
    if (indexable) {
        PyErr_SetString(PyExc_IndexError, "too many indices");
    }
    else {
        PyErr_SetString(PyExc_TypeError, "type not indexable");
    }
}

/*
 * Return a zero copy view of an xnd object.  If a dtype is indexable,
 * descend into the dtype.
 */
static xnd_t
pyxnd_subtree(const xnd_t *x, PyObject *indices[], int len, bool indexable)
{
    NDT_STATIC_CONTEXT(ctx);
    const ndt_t *t = x->type;
    PyObject *key;

    assert(ndt_is_concrete(t));

    if (t->ndim > 0 && ndt_is_optional(t)) {
        PyErr_SetString(PyExc_NotImplementedError,
            "optional dimensions are not supported");
        return xnd_error;
    }

    if (len == 0) {
        return *x;
    }

    key = indices[0];

    switch (t->tag) {
    case FixedDim: {
        int64_t i = get_index(key, t->FixedDim.shape);
        if (i < 0) {
            return xnd_error;
        }

        const xnd_t next = xnd_fixed_dim_next(x, i);
        return pyxnd_subtree(&next, indices+1, len-1, true);
    }

    case VarDim: {
        int64_t start, step, shape;
        int64_t i;

        shape = ndt_var_indices(&start, &step, t, x->index, &ctx);
        if (shape < 0) {
            return seterr_xnd(&ctx);
        }

        i = get_index(key, shape);
        if (i < 0) {
            return xnd_error;
        }

        const xnd_t next = xnd_var_dim_next(x, start, step, i);
        return pyxnd_subtree(&next, indices+1, len-1, true);
    }

    case Tuple: {
        const int64_t i = get_index(key, t->Tuple.shape);
        if (i < 0) {
            return xnd_error;
        }

        const xnd_t next = xnd_tuple_next(x, i, &ctx);
        if (next.ptr == NULL) {
            return seterr_xnd(&ctx);
        }

        return pyxnd_subtree(&next, indices+1, len-1, true);
    }

    case Record: {
        int64_t i = get_index_record(t, key);
        if (i < 0) {
            return xnd_error;
        }

        const xnd_t next = xnd_record_next(x, i, &ctx);
        if (next.ptr == NULL) {
            return seterr_xnd(&ctx);
        }

        return pyxnd_subtree(&next, indices+1, len-1, true);
    }

    case Ref: {
        const xnd_t next = xnd_ref_next(x, &ctx);
        if (next.ptr == NULL) {
            return seterr_xnd(&ctx);
        }

        return pyxnd_subtree(&next, indices, len, false);
    }

    case Constr: {
        const xnd_t next = xnd_constr_next(x, &ctx);
        if (next.ptr == NULL) {
            return seterr_xnd(&ctx);
        }

        return pyxnd_subtree(&next, indices, len, false);
    }

    case Nominal: {
        const xnd_t next = xnd_nominal_next(x, &ctx);
        if (next.ptr == NULL) {
            return seterr_xnd(&ctx);
        }

        return pyxnd_subtree(&next, indices, len, false);
    }

    default:
        set_index_exception(indexable);
        return xnd_error;
    }
}

static xnd_t pyxnd_index(const xnd_t *x, PyObject *indices[], int len);
static xnd_t pyxnd_slice(const xnd_t *x, PyObject *indices[], int len);

static xnd_t
pyxnd_multikey(const xnd_t *x, PyObject *indices[], int len)
{
    NDT_STATIC_CONTEXT(ctx);
    const ndt_t *t = x->type;
    PyObject *key;

    assert(len >= 0);
    assert(ndt_is_concrete(t));
    assert(x->ptr != NULL);

    if (len > t->ndim) {
        PyErr_SetString(PyExc_IndexError, "too many indices");
        return xnd_error;
    }

    if (len == 0) {
        xnd_t next = *x;
        next.type = ndt_copy(t, &ctx);
        if (next.type == NULL) {
            return seterr_xnd(&ctx);
        }

        return next;
    }

    key = indices[0];

    if (PyIndex_Check(key)) {
        return pyxnd_index(x, indices, len);
    }
    else if (PySlice_Check(key)) {
        return pyxnd_slice(x, indices, len);
    }

    PyErr_SetString(PyExc_RuntimeError,
        "multikey: internal error: key must be index or slice");

    return xnd_error;
}

/*
 * Return a view with a copy of the type.  Indexing into the dtype is
 * not permitted.
 */
static xnd_t
pyxnd_index(const xnd_t *x, PyObject *indices[], int len)
{
    const ndt_t *t = x->type;
    PyObject *key;

    assert(len > 0);
    assert(PyIndex_Check(indices[0]));
    assert(ndt_is_concrete(t));
    assert(x->ptr != NULL);

    key = indices[0];

    switch (t->tag) {
    case FixedDim: {
        const int64_t i = get_index(key, t->FixedDim.shape);
        if (i < 0) {
            return xnd_error;
        }

        const xnd_t next = xnd_fixed_dim_next(x, i);
        return pyxnd_multikey(&next, indices+1, len-1);
    }

    case VarDim: {
        PyErr_SetString(PyExc_IndexError,
            "mixed indexing and slicing is not supported for var dimensions");
        return xnd_error;
    }

    default:
        PyErr_SetString(PyExc_IndexError, "type is not indexable");
        return xnd_error;
    }
}

static xnd_t
pyxnd_slice(const xnd_t *x, PyObject *indices[], int len)
{
    NDT_STATIC_CONTEXT(ctx);
    const ndt_t *t = x->type;
    PyObject *key;

    assert(len > 0);
    assert(PySlice_Check(indices[0]));
    assert(ndt_is_concrete(t));
    assert(x->ptr != NULL);

    key = indices[0];

    switch (t->tag) {
    case FixedDim: {
        int64_t start, stop, step, shape;
        if (py_slice_get_indices_ex(key, t->FixedDim.shape,
                                    &start, &stop, &step, &shape) < 0) {
            return xnd_error;
        }

        const xnd_t next = xnd_fixed_dim_next(x, start);
        const xnd_t sliced = pyxnd_multikey(&next, indices+1, len-1);
        if (sliced.ptr == NULL) {
            return xnd_error;
        }

        xnd_t ret = *x;
        ret.type = ndt_fixed_dim((ndt_t *)sliced.type, shape,
                                 t->Concrete.FixedDim.step * step,
                                 &ctx);
        if (ret.type == NULL) {
            return seterr_xnd(&ctx);
        }
        ret.index = sliced.index;

        return ret;
    }

    case VarDim: {
        Py_ssize_t start, stop, step;
        ndt_slice_t *slices;
        int32_t nslices;

        if (ndt_is_optional(t)) {
            PyErr_SetString(PyExc_NotImplementedError,
                "optional dimensions are temporarily disabled");
            return xnd_error;
        }

        if (pyslice_unpack(key, &start, &stop, &step) < 0) {
            return xnd_error;
        }

        xnd_t next = *x;
        next.type = t->VarDim.type;

        next = pyxnd_multikey(&next, indices+1, len-1);
        if (next.ptr == NULL) {
            return xnd_error;
        }

        slices = ndt_var_add_slice(&nslices, t, start, stop, step, &ctx);
        if (slices == NULL) {
            return seterr_xnd(&ctx);
        }

        xnd_t ret = *x;
        ret.type = ndt_var_dim((ndt_t *)next.type,
                                ExternalOffsets,
                                t->Concrete.VarDim.noffsets, t->Concrete.VarDim.offsets,
                                nslices, slices,
                                &ctx);
        if (ret.type == NULL) {
            return seterr_xnd(&ctx);
        }

        ret.index = next.index;

        return ret;
    }

    case Tuple: {
        PyErr_SetString(PyExc_NotImplementedError,
            "slicing tuples is not supported");
        return xnd_error;
    }

    case Record: {
        PyErr_SetString(PyExc_NotImplementedError,
            "slicing records is not supported");
        return xnd_error;
    }

    default:
        PyErr_SetString(PyExc_IndexError, "type not sliceable");
        return xnd_error;
    }
}

static int
is_multiindex(const PyObject *key)
{
    Py_ssize_t size, i;

    if (!PyTuple_Check(key)) {
        return 0;
    }

    size = PyTuple_GET_SIZE(key);
    for (i = 0; i < size; i++) {
        PyObject *x = PyTuple_GET_ITEM(key, i);
        if (!PyIndex_Check(x)) {
            return 0;
        }
    }

    return 1;
}

static int
is_multikey(const PyObject *key)
{
    Py_ssize_t size, i;

    if (!PyTuple_Check(key)) {
        return 0;
    }

    size = PyTuple_GET_SIZE(key);
    for (i = 0; i < size; i++) {
        PyObject *x = PyTuple_GET_ITEM(key, i);
        if (!PyIndex_Check(x) && !PySlice_Check(x)) {
            return 0;
        }
    }

    return 1;
}

static PyObject *
value_or_view_copy(XndObject *self, const xnd_t *x)
{
    if (x->ptr == NULL) {
        return NULL;
    }

    if (x->type->ndim == 0) {
        switch (x->type->tag) {
        case Tuple: case Record: case Ref: case Constr: case Nominal:
            return pyxnd_view_copy_type(self, x);
        default:
            return _pyxnd_value(x, INT64_MAX);
        }
    }

    return pyxnd_view_copy_type(self, x);
}

static PyObject *
value_or_view_move(XndObject *self, xnd_t *x)
{
    if (x->ptr == NULL) {
        return NULL;
    }

    if (x->type->ndim == 0) {
        switch (x->type->tag) {
        case Tuple: case Record: case Ref: case Constr: case Nominal:
            return pyxnd_view_move_type(self, x);
        default:
            return _pyxnd_value(x, INT64_MAX);
        }
    }

    return pyxnd_view_move_type(self, x);
}

static PyObject *
pyxnd_subscript(XndObject *self, PyObject *key)
{
    if (PyIndex_Check(key) || PyUnicode_Check(key)) {
        PyObject *indices[1] = {key};
        const xnd_t x = pyxnd_subtree(&self->xnd, indices, 1, false);
        return value_or_view_copy(self, &x);
    }
    else if (is_multiindex(key)) {
        PyObject **indices = &PyTuple_GET_ITEM(key, 0);
        Py_ssize_t n = PyTuple_GET_SIZE(key);
        if (n > INT_MAX) {
            goto value_error;
        }
        const xnd_t x = pyxnd_subtree(&self->xnd, indices, (int)n, false);
        return value_or_view_copy(self, &x);
    }
    else if (PySlice_Check(key)) {
        PyObject *indices[1] = {key};
        xnd_t x = pyxnd_multikey(&self->xnd, indices, 1);
        return value_or_view_move(self, &x);
    }
    else if (is_multikey(key)) {
        PyObject **indices = &PyTuple_GET_ITEM(key, 0);
        Py_ssize_t n = PyTuple_GET_SIZE(key);
        if (n > INT_MAX) {
            goto value_error;
        }
        xnd_t x = pyxnd_multikey(&self->xnd, indices, (int)n);
        return value_or_view_move(self, &x);
    }
    else {
        PyErr_SetString(PyExc_TypeError, "invalid subscript key");
        return NULL;
    }

value_error:
    PyErr_SetString(PyExc_ValueError, "too many indices");
    return NULL;
}

static int
pyxnd_assign(XndObject *self, PyObject *key, PyObject *value)
{
    int free_type = 0;
    xnd_t x;
    int ret;

    if (value == NULL) {
        PyErr_SetString(PyExc_TypeError, "cannot delete memory blocks");
        return -1;
    }

    if (is_readonly(self)) {
        PyErr_SetString(PyExc_TypeError, "memory block is read-only");
        return -1;
    }

    if (PyIndex_Check(key) || PyUnicode_Check(key)) {
        PyObject *indices[1] = {key};
        x = pyxnd_subtree(&self->xnd, indices, 1, false);
    }
    else if (is_multiindex(key)) {
        PyObject **indices = &PyTuple_GET_ITEM(key, 0);
        Py_ssize_t n = PyTuple_GET_SIZE(key);
        if (n > INT_MAX) {
            goto value_error;
        }
        x = pyxnd_subtree(&self->xnd, indices, (int)n, false);
    }
    else if (PySlice_Check(key)) {
        PyObject *indices[1] = {key};
        x = pyxnd_multikey(&self->xnd, indices, 1);
        free_type = 1;
    }
    else if (is_multikey(key)) {
        PyObject **indices = &PyTuple_GET_ITEM(key, 0);
        Py_ssize_t n = PyTuple_GET_SIZE(key);
        if (n > INT_MAX) {
            goto value_error;
        }
        x = pyxnd_multikey(&self->xnd, indices, (int)n);
        free_type = 1;
    }
    else {
        PyErr_SetString(PyExc_TypeError, "invalid subscript key");
        return -1;
    }

    if (x.ptr == NULL) {
        return -1;
    }

    ret = mblock_init(&x, value);
    if (free_type) {
        ndt_del((ndt_t *)x.type);
    }

    return ret;

value_error:
    PyErr_SetString(PyExc_ValueError, "too many indices");
    return -1;
}

static PyObject *
pyxnd_item(XndObject *self, Py_ssize_t index)
{
    PyObject *res;
    PyObject *key;

    key = PyLong_FromSsize_t(index);
    if (key == NULL) {
        return NULL;
    }

    res = pyxnd_subscript(self, key);
    Py_DECREF(key);
    return res;
}

static PyObject *
pyxnd_short_value(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"maxshape", NULL};
    PyObject *maxshape = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O", kwlist, &maxshape)) {
        return NULL;
    }

    if (maxshape == Py_None) {
        return _pyxnd_value(XND(self), INT64_MAX);
    }
    else {
        Py_ssize_t max = PyLong_AsSsize_t(maxshape);
        if (max == -1 && PyErr_Occurred()) {
            return NULL;
        }
        if (max < 0) {
            PyErr_SetString(PyExc_ValueError, "maxshape must be positive");
            return NULL;
        }

        return _pyxnd_value(XND(self), max);
    }
}

static PyObject *
pyxnd_type(PyObject *self, PyObject *args UNUSED)
{
    Py_INCREF(TYPE_OWNER(self));
    return TYPE_OWNER(self);
}

static PyObject *
pyxnd_ndim(PyObject *self, PyObject *args UNUSED)
{
    int ndim = XND_TYPE(self)->ndim;
    return PyLong_FromLong(ndim);
}

static PyObject *
pyxnd_value(PyObject *self, PyObject *args UNUSED)
{
    return _pyxnd_value(XND(self), INT64_MAX);
}

static PyObject *
pyxnd_align(PyObject *self, PyObject *args UNUSED)
{
    uint16_t align = XND_TYPE(self)->align;
    return PyLong_FromUnsignedLong(align);
}


static PyGetSetDef pyxnd_getsets [] =
{
  { "type", (getter)pyxnd_type, NULL, doc_type, NULL},
  { "value", (getter)pyxnd_value, NULL, doc_value, NULL},
  { "align", (getter)pyxnd_align, NULL, doc_align, NULL},
  { "ndim", (getter)pyxnd_ndim, NULL, doc_ndim, NULL},
  {NULL}
};

static PyMappingMethods pyxnd_as_mapping = {
    (lenfunc)pyxnd_length,         /* mp_length */
    (binaryfunc)pyxnd_subscript,   /* mp_subscript */
    (objobjargproc)pyxnd_assign,   /* mp_ass_subscript */
};

static PySequenceMethods pyxnd_as_sequence = {
    (lenfunc)pyxnd_length,         /* sq_length */
    0,                             /* sq_concat */
    0,                             /* sq_repeat */
    (ssizeargfunc)pyxnd_item,      /* sq_item */
};


static PyMethodDef pyxnd_methods [] =
{
  /* Methods */
  { "short_value", (PyCFunction)pyxnd_short_value, METH_VARARGS|METH_KEYWORDS, doc_short_value },

  /* Class methods */
  { "empty", (PyCFunction)pyxnd_empty, METH_O|METH_CLASS, doc_empty },
  { "from_buffer", (PyCFunction)pyxnd_from_buffer, METH_O|METH_CLASS, doc_from_buffer },

  { NULL, NULL, 1 }
};


/****************************************************************************/
/*                              Buffer exports                              */
/****************************************************************************/

static PyTypeObject BufferProxy_Type;

typedef struct {
    PyObject_HEAD
    XndObject *xnd;
    Py_buffer view;
    Py_ssize_t ob_array[1];
} BufferProxyObject;

static BufferProxyObject *
buffer_alloc(XndObject *xnd)
{
    const ndt_t *t = XND_TYPE(xnd);
    BufferProxyObject *self;

    self = (BufferProxyObject *)
        PyObject_NewVar(BufferProxyObject, &BufferProxy_Type, 2 * t->ndim);
    if (self == NULL) {
        return NULL;
    }

    Py_INCREF(xnd);
    self->xnd = xnd;
 
    self->view.buf = NULL;
    self->view.obj = NULL;
    self->view.len = 0;
    self->view.itemsize = 0;
    self->view.readonly = 0;

    self->view.ndim = t->ndim;
    self->view.format = NULL;
    self->view.shape = self->ob_array;
    self->view.strides = self->ob_array + t->ndim;
    self->view.suboffsets = NULL;
    self->view.internal = NULL;

    return self;
}

static void
buffer_dealloc(BufferProxyObject *self)
{
    ndt_free(self->view.format);
    self->view.format = NULL;
    Py_CLEAR(self->xnd);
    PyObject_Del(self);
}

static int
fill_buffer(Py_buffer *view, const xnd_t *x, ndt_context_t *ctx)
{
    const ndt_t *t = x->type;
    char *fmt;
    Py_ssize_t len;
    int i;

    assert(t->ndim <= NDT_MAX_DIM);
    assert(ndt_is_concrete(t));

    fmt = ndt_to_bpformat(ndt_dtype(t), ctx);
    if (fmt == NULL) {
        return -1;
    }

    view->ndim = t->ndim;
    view->format = fmt;
    view->suboffsets = NULL;

    if (!ndt_is_ndarray(t)) {
        if (t->ndim == 0) {
            view->len = t->datasize;
            view->itemsize = t->datasize;
            view->shape = NULL;
            view->strides = NULL;
            view->buf = x->ptr + x->index * t->datasize;
            return 0;
        }
        else {
            ndt_err_format(ctx, NDT_ValueError,
                "buffer protocol only supports ndarrays");
            return -1;
        }
    }

    view->itemsize = t->Concrete.FixedDim.itemsize;
    view->buf = x->ptr + x->index * view->itemsize;

    len = 1;
    for (i=0; t->ndim > 0; i++, t=t->FixedDim.type) {
        view->shape[i] = t->FixedDim.shape;
        view->strides[i] = t->Concrete.FixedDim.step * view->itemsize;
        len *= view->shape[i];
    }
    len *=  view->itemsize;

    view->len = len;

    return 0;
}

static int
pyxnd_getbuf(XndObject *self, Py_buffer *view, int flags)
{
    NDT_STATIC_CONTEXT(ctx);
    BufferProxyObject *proxy;

    if (flags != PyBUF_FULL && flags != PyBUF_FULL_RO) {
        PyErr_SetString(PyExc_ValueError,
            "only PyBUF_FULL and PyBUF_FULL_RO requests are supported");
        return -1;
    }

    proxy = buffer_alloc(self);
    if (proxy == NULL) {
        return -1;
    }

    if (fill_buffer(&proxy->view, XND(self), &ctx) < 0) {
        Py_DECREF(proxy);
        return seterr_int(&ctx);
    }

    *view = proxy->view;
    view->obj = (PyObject *)proxy;

    return 0;
}

static void
pyxnd_releasebuf(XndObject *self UNUSED, Py_buffer *view UNUSED)
{
    return;
    /* PyBuffer_Release() decrements view->obj after this function returns. */
}


static PyTypeObject BufferProxy_Type =
{
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "xnd.BufferProxy",
    .tp_basicsize = offsetof(BufferProxyObject, ob_array),
    .tp_itemsize = sizeof(Py_ssize_t),
    .tp_dealloc = (destructor) buffer_dealloc,
    .tp_hash = PyObject_HashNotImplemented,
    .tp_getattro = (getattrofunc) PyObject_GenericGetAttr,
    .tp_flags = Py_TPFLAGS_DEFAULT,
};

static PyBufferProcs pyxnd_as_buffer = {
    (getbufferproc)pyxnd_getbuf,         /* bf_getbuffer */
    (releasebufferproc)pyxnd_releasebuf, /* bf_releasebuffer */
};


/****************************************************************************/
/*                                 Xnd type                                 */
/****************************************************************************/

static PyTypeObject Xnd_Type =
{
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "xnd.Xnd",
    .tp_basicsize = sizeof(XndObject),
    .tp_dealloc = (destructor) pyxnd_dealloc,
    .tp_as_sequence = &pyxnd_as_sequence,
    .tp_as_mapping = &pyxnd_as_mapping,
    .tp_hash = PyObject_HashNotImplemented,
    .tp_getattro = (getattrofunc) PyObject_GenericGetAttr,
    .tp_as_buffer = &pyxnd_as_buffer,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_traverse = (traverseproc)pyxnd_traverse,
    .tp_methods = pyxnd_methods,
    .tp_getset = pyxnd_getsets,
    .tp_alloc = PyType_GenericAlloc,
    .tp_new = pyxnd_new,
    .tp_free = PyObject_GC_Del
};


/****************************************************************************/
/*                                   C-API                                  */
/****************************************************************************/

static void **xnd_api[XND_MAX_API];

static int
Xnd_CheckExact(const PyObject *v)
{
    return Py_TYPE(v) == &Xnd_Type;
}

static int
Xnd_Check(const PyObject *v)
{
    return PyObject_TypeCheck(v, &Xnd_Type);
}

static const xnd_t *
CONST_XND(const PyObject *v)
{
    assert(Xnd_Check(v));
    return &((XndObject *)v)->xnd;
}

static PyObject *
Xnd_EmptyFromType(PyTypeObject *tp, ndt_t *t)
{
    MemoryBlockObject *mblock;
    PyObject *type;

    type = Ndt_FromType(t);
    if (type == NULL) {
        return NULL;
    }

    mblock = mblock_empty(type);
    Py_DECREF(type);
    if (mblock == NULL) {
        return NULL;
    }

    return pyxnd_from_mblock(tp, mblock);
}

static PyObject *
Xnd_ViewMoveNdt(const PyObject *v, ndt_t *t)
{
    XndObject *src = (XndObject *)v;
    XndObject *view;
    PyObject *type;

    if (!Xnd_Check(v)) {
        PyErr_SetString(PyExc_TypeError, "expected xnd object");
        ndt_del(t);
        return NULL;
    }

    type = Ndt_MoveSubtree(src->type, t);
    if (type == NULL) {
        return NULL;
    }

    view = pyxnd_alloc(Py_TYPE(src));
    if (view == NULL) {
        Py_DECREF(type);
        return NULL;
    }

    Py_INCREF(src->mblock);
    view->mblock = src->mblock;
    view->type = type;
    view->xnd = src->xnd;
    view->xnd.type = t;

    return (PyObject *)view;
}

static PyObject *
Xnd_FromXnd(PyTypeObject *tp, xnd_t *x)
{
    MemoryBlockObject *mblock;

    mblock = mblock_from_xnd(x);
    if (mblock == NULL) {
        return NULL;
    }

    return pyxnd_from_mblock(tp, mblock);
}


static PyObject *
init_api(void)
{
    xnd_api[Xnd_CheckExact_INDEX] = (void *)Xnd_CheckExact;
    xnd_api[Xnd_Check_INDEX] = (void *)Xnd_Check;
    xnd_api[CONST_XND_INDEX] = (void *)CONST_XND;
    xnd_api[Xnd_EmptyFromType_INDEX] = (void *)Xnd_EmptyFromType;
    xnd_api[Xnd_ViewMoveNdt_INDEX] = (void *)Xnd_ViewMoveNdt;
    xnd_api[Xnd_FromXnd_INDEX] = (void *)Xnd_FromXnd;

    return PyCapsule_New(xnd_api, "xnd._xnd._API", NULL);
}


/****************************************************************************/
/*                                  Module                                  */
/****************************************************************************/



static struct PyModuleDef xnd_module = {
    PyModuleDef_HEAD_INIT,        /* m_base */
    "_xnd",                       /* m_name */
    doc_module,                   /* m_doc */
    -1,                           /* m_size */
    NULL,                         /* m_methods */
    NULL,                         /* m_slots */
    NULL,                         /* m_traverse */
    NULL,                         /* m_clear */
    NULL                          /* m_free */
};


PyMODINIT_FUNC
PyInit__xnd(void)
{
    PyObject *m = NULL;
    static PyObject *capsule = NULL;
    static int initialized = 0;

    if (!initialized) {
        if (import_ndtypes() < 0) {
            return NULL;
        }
        capsule = init_api();
        if (capsule == NULL) {
            return NULL;
        }
        initialized = 1;
    }

    if (PyType_Ready(&XndEllipsis_Type) < 0) {
        return NULL;
    }

    if (PyType_Ready(&MemoryBlock_Type) < 0) {
        return NULL;
    }

    if (PyType_Ready(&BufferProxy_Type) < 0) {
        return NULL;
    }

    Xnd_Type.tp_base = &PyBaseObject_Type;
    if (PyType_Ready(&Xnd_Type) < 0) {
        return NULL;
    }

    m = PyModule_Create(&xnd_module);
    if (m == NULL) {
        goto error;
    }

    if (PyModule_AddObject(m, "XndEllipsis", xnd_ellipsis()) < 0) {
        goto error;
    }

    Py_INCREF(&Xnd_Type);
    if (PyModule_AddObject(m, "Xnd", (PyObject *)&Xnd_Type) < 0) {
        goto error;
    }

    Py_INCREF(capsule);
    if (PyModule_AddObject(m, "_API", capsule) < 0) {
        goto error;
    }

    return m;

error:
    Py_CLEAR(m);
    return NULL;
}


