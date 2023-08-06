.. meta::
   :robots: index,follow
   :description: xnd container
   :keywords: xnd, types, examples

.. sectionauthor:: Stefan Krah <skrah at bytereef.org>


Types
=====

The xnd object is a container that maps a wide range of Python values directly
to memory.  xnd unpacks complex types of arbitrary nesting depth to a single
memory block.

Pointers only occur in explicit pointer types like *Ref* (reference), *Bytes*
and *String*, but not in the general case.


Type inference
--------------

If no explicit type is given, xnd supports type inference by assuming
types for the most common Python values.


Fixed arrays
~~~~~~~~~~~~

.. doctest::

   >>> from xnd import *
   >>> x = xnd([[0, 1, 2], [3, 4, 5]])
   >>> x
   xnd([[0, 1, 2], [3, 4, 5]], type='2 * 3 * int64')


As expected, lists are mapped to ndarrays and integers to int64.  Indexing and
slicing works the usual way.  For performance reasons these operations return
zero-copy views whenever possible:

.. doctest::

   >>> x[0][1] # Scalars are returned as Python values.
   1
   >>>
   >>> y = x[:, ::-1] # Containers are returned as views.
   >>> y
   xnd([[2, 1, 0], [5, 4, 3]], type='2 * 3 * int64')


Subarrays are views and properly typed:

.. doctest::

   >>> x[1]
   xnd([3, 4, 5], type='3 * int64')


The representation of large values is abbreviated:

.. doctest::

   >>> x = xnd(10 * [200 * [1]])
   >>> x
   xnd([[1, 1, 1, 1, 1, 1, 1, 1, 1, ...],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, ...],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, ...],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, ...],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, ...],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, ...],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, ...],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, ...],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, ...],
        ...],
       type='10 * 200 * int64')


Values can be accessed in full using the *value* property:

.. doctest::

   >>> x = xnd(11 * [1])
   >>> x
   xnd([1, 1, 1, 1, 1, 1, 1, 1, 1, ...], type='11 * int64')
   >>> x.value
   [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


Types can be accessed using the *type* property:

.. doctest::

   >>> x = xnd(11 * [1])
   >>> x.type
   ndt("11 * int64")


Ragged arrays
~~~~~~~~~~~~~

Ragged arrays are compatible with the Arrow list representation. The data
is pointer-free, addressing the elements works by having one offset array
per dimension.

.. doctest::

   >>> xnd([[0.1j], [3+2j, 4+5j, 10j]])
   xnd([[0.1j], [(3+2j), (4+5j), 10j]], type='var * var * complex128')


Indexing and slicing works as usual, returning properly typed views or
values in the case of scalars:

.. doctest::

   >>> x = xnd([[0.1j], [3+2j, 4+5j, 10j]])
   >>> x[1, 2]
   10j

   >>> x[1]
   xnd([(3+2j), (4+5j), 10j], type='var * complex128')


Eliminating dimensions through mixed slicing and indexing is not supported
because it would require copying and adjusting potentially huge offset arrays:

.. doctest::

   >>> y = x[:, 1]
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   IndexError: mixed indexing and slicing is not supported for var dimensions


Records (structs)
~~~~~~~~~~~~~~~~~

From Python 3.6 on, dicts retain their order, so they can be used directly
for initializing C structs.

.. doctest::

   >>> xnd({'a': 'foo', 'b': 10.2})
   xnd({'a': 'foo', 'b': 10.2}, type='{a : string, b : float64}')


Tuples
~~~~~~

Python tuples are directly translated to the libndtypes tuple type:

.. doctest::

   >>> xnd(('foo', b'bar', [None, 10.0, 20.0]))
   xnd(('foo', b'bar', [None, 10.0, 20.0]), type='(string, bytes, 3 * ?float64)')


Nested arrays in structs
~~~~~~~~~~~~~~~~~~~~~~~~

xnd seamlessly supports nested values of arbitrary depth:

.. doctest::

   >>> lst = [{'name': 'John', 'internet_points': [1, 2, 3]},
   ...        {'name': 'Jane', 'internet_points': [4, 5, 6]}]
   >>> xnd(lst)
   xnd([{'name': 'John', 'internet_points': [1, 2, 3]}, {'name': 'Jane', 'internet_points': [4, 5, 6]}],
       type='2 * {name : string, internet_points : 3 * int64}')


Optional data (missing values)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optional data is currently specified using *None*.  It is under debate if
a separate *NA* singleton object would be more suitable.

.. doctest::

   >>> lst = [0, 1, None, 2, 3, None, 5, 10]
   >>> xnd(lst)
   xnd([0, 1, None, 2, 3, None, 5, 10], type='8 * ?int64')


Categorical data
~~~~~~~~~~~~~~~~

Type inference would be ambiguous, so it cannot work directly. xnd supports
the *levels* argument that is internally translated to the type.

.. doctest::

   >>> levels = ['January', 'August', 'December', None]
   >>> x = xnd(['January', 'January', None, 'December', 'August', 'December', 'December'], levels=levels)
   >>> x.value
   ['January', 'January', None, 'December', 'August', 'December', 'December']
   >>> x.type
   ndt("7 * categorical('January', 'August', 'December', NA)")


The above is equivalent to specifying the type directly:

.. doctest::

   >>> from ndtypes import *
   >>> t = ndt("7 * categorical('January', 'August', 'December', NA)")
   >>> x = xnd(['January', 'January', None, 'December', 'August', 'December', 'December'], type=t)
   >>> x.value
   ['January', 'January', None, 'December', 'August', 'December', 'December']
   >>> x.type
   ndt("7 * categorical('January', 'August', 'December', NA)")


Explicit types
--------------

While type inference is well-defined, it necessarily makes assumptions about
the programmer's intent.

There are two cases where types should be given:


Different types are intended
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. doctest::

   >>> xnd([[0,1,2], [3,4,5]], type="2 * 3 * uint8")
   xnd([[0, 1, 2], [3, 4, 5]], type='2 * 3 * uint8')

Here, type inference would deduce :c:macro:`int64`, so :c:macro:`uint8` needs
to be passed explicitly.


Performance
~~~~~~~~~~~

For large arrays, explicit types are significantly faster.  Type inference
supports arbitrary nesting depth, is complex and still implemented in pure
Python. Compare:

.. doctest::

   >>> lst = [1] * 1000000
   >>> x = xnd(lst) # inference
   >>>
   >>> x = xnd(lst, type='1000000 * int64') # explicit


All supported types
-------------------

Fixed arrays
~~~~~~~~~~~~

Fixed arrays are similar to NumPy's ndarray. One difference is that internally
xnd uses steps instead of strides. One step is the amount of indices required
to move the linear index from one dimension element to the next.

This facilitates optional data, whose bitmaps need to be addressed by the
linear index.  The equation *stride = step * itemsize* always holds.


.. doctest::

   >>> xnd([[[1,2], [None, 3]], [[4, None], [5, 6]]])
   xnd([[[1, 2], [None, 3]], [[4, None], [5, 6]]], type='2 * 2 * 2 * ?int64')

This is a fixed array with optional data.


.. doctest::

   >>> xnd([(1,2.0,3j), (4,5.0,6j)])
   xnd([(1, 2.0, 3j), (4, 5.0, 6j)], type='2 * (int64, float64, complex128)')

An array with tuple elements.


Fortran order
~~~~~~~~~~~~~

Fortran order is specified by prefixing the dimensions with an exclamation mark:

.. doctest::

   >>> lst = [[1, 2, 3], [4, 5, 6]]
   >>> x = xnd(lst, type='!2 * 3 * uint16')
   >>> 
   >>> x.type.shape
   (2, 3)
   >>> x.type.strides
   (2, 4)


Alternatively, steps can be passed as arguments to the fixed dimension type:

.. doctest::

   >>> from ndtypes import *
   >>> lst = [[1, 2, 3], [4, 5, 6]]
   >>> t = ndt("fixed(shape=2, step=1) * fixed(shape=3, step=2) * uint16")
   >>> x = xnd(lst, type=t)
   >>> x.type.shape
   (2, 3)
   >>> x.type.strides
   (2, 4)


Ragged arrays
~~~~~~~~~~~~~

Ragged arrays with explicit types are easiest to construct using the *dtype*
argument to the xnd constructor.

.. doctest::

   >>> lst = [[0], [1, 2], [3, 4, 5]]
   >>> xnd(lst, dtype="int32")
   xnd([[0], [1, 2], [3, 4, 5]], type='var * var * int32')


Alternatively, offsets can be passed as arguments to the var dimension type:

.. doctest::

   >>> from ndtypes import ndt
   >>> t = ndt("var(offsets=[0,3]) * var(offsets=[0,1,3,6]) * int32")
   >>> xnd(lst, type=t)
   xnd([[0], [1, 2], [3, 4, 5]], type='var * var * int32')


Tuples
~~~~~~

In memory, tuples are the same as C structs.

.. doctest::

   >>> xnd(("foo", 1.0))
   xnd(('foo', 1.0), type='(string, float64)')


Indexing works the same as for arrays:

.. doctest::

   >>> x = xnd(("foo", 1.0))
   >>> x[0]
   'foo'


Nested tuples are more general than ragged arrays. They can a) hold different
data types and b) the trees they represent may be unbalanced.

They do not allow slicing though and are probably less efficient.

This is an example of an unbalanced tree that cannot be represented as a
ragged array:

.. doctest::

   >>> unbalanced_tree = (((1.0, 2.0), (3.0)), 4.0, ((5.0, 6.0, 7.0), ()))
   >>> x = xnd(unbalanced_tree)
   >>> x.value
   (((1.0, 2.0), 3.0), 4.0, ((5.0, 6.0, 7.0), ()))
   >>> x.type
   ndt("(((float64, float64), float64), float64, ((float64, float64, float64), ()))")
   >>> 
   >>> x[0]
   xnd(((1.0, 2.0), 3.0), type='((float64, float64), float64)')
   >>> x[0][0]
   xnd((1.0, 2.0), type='(float64, float64)')


Note that the data in the above tree example is packed into a single contiguous
memory block.


Records
~~~~~~~

In memory, records are C structs. The field names are only stored in the type.

The following examples use Python-3.6, which keeps the dict initialization
order.

.. doctest::

   >>> x = xnd({'a': b'123', 'b': {'x': 1.2, 'y': 100+3j}})
   >>> x.value
   {'a': b'123', 'b': {'x': 1.2, 'y': (100+3j)}}
   >>> x.type
   ndt("{a : bytes, b : {x : float64, y : complex128}}")


Indexing works the same as for arrays. Additionally, fields can be indexed
by name:

.. doctest::

   >>> x[0]
   b'123'
   >>> x['a']
   b'123'
   >>> x['b']
   xnd({'x': 1.2, 'y': (100+3j)}, type='{x : float64, y : complex128}')


The nesting depth is arbitrary.  In the following example, the data -- except
for strings, which are pointers -- is packed into a single contiguous memory
block:

.. code-block:: py

   >>> from pprint import pprint
   >>> item = {
   ...   "id": 1001,
   ...   "name": "cyclotron",
   ...   "price": 5998321.99,
   ...   "tags": ["connoisseur", "luxury"],
   ...   "stock": {
   ...     "warehouse": 722,
   ...     "retail": 20
   ...   }
   ... }
   >>> x = xnd(item)
   >>>
   >>> pprint(x.value)
   {'id': 1001,
    'name': 'cyclotron',
    'price': 5998321.99,
    'stock': {'retail': 20, 'warehouse': 722},
    'tags': ['connoisseur', 'luxury']}
   >>>
   >>> x.type.pprint()
   {
     id : int64,
     name : string,
     price : float64,
     tags : 2 * string,
     stock : {
       warehouse : int64,
       retail : int64
     }
   }


Strings can be embedded into the array by specifying the fixed string type.
In this case, the memory block is pointer-free.

.. code-block:: py

   >>> from ndtypes import ndt
   >>> 
   >>> t = """
   ...   { id : int64,
   ...     name : fixed_string(30),
   ...     price : float64,
   ...     tags : 2 * fixed_string(30),
   ...     stock : {warehouse : int64, retail : int64} 
   ...   }
   ... """
   >>> 
   >>> x = xnd(item, type=t)
   >>> x.type.pprint()
   {
     id : int64,
     name : fixed_string(30),
     price : float64,
     tags : 2 * fixed_string(30),
     stock : {
       warehouse : int64,
       retail : int64
     }
   }


Record of arrays
~~~~~~~~~~~~~~~~

Often it is more memory efficient to store an array of records as a record of
arrays.  This example with columnar data is from the Arrow homepage:

.. doctest::

   >>> data = {'session_id': [1331247700, 1331247702, 1331247709, 1331247799],
   ...         'timestamp': [1515529735.4895875, 1515529746.2128427, 1515529756.4485607, 1515529766.2181058],
   ...         'source_ip': ['8.8.8.100', '100.2.0.11', '99.101.22.222', '12.100.111.200']}
   >>> x = xnd(data)
   >>> x.type
   ndt("{session_id : 4 * int64, timestamp : 4 * float64, source_ip : 4 * string}")



References
~~~~~~~~~~

References are transparent pointers to new memory blocks (meaning a new
data pointer, not a whole new xnd buffer).

For example, this is an array of pointer to array:

.. doctest::

   >>> t = ndt("3 * ref(4 * uint64)")
   >>> lst = [[0,1,2,3], [4,5,6,7], [8,9,10,11]]
   >>> xnd(lst, type=t)
   xnd([[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]], type='3 * ref(4 * uint64)')

The user sees no difference to a regular 3 by 4 array, but internally
the outer dimension consists of three pointers to the inner arrays.

For memory blocks generated by xnd itself the feature is not so useful --
after all, it is usually better to have a single memory block than one
with additional pointers.


However, suppose that in the above columnar data example another application
represents the arrays inside the record with pointers.  Using the *ref* type,
data structures borrowed from such an application can be properly typed:

.. doctest::

   >>> t = ndt("{session_id : &4 * int64, timestamp : &4 * float64, source_ip : &4 * string}")
   >>> x = xnd(data, type=t)
   >>> x.type
   ndt("{session_id : ref(4 * int64), timestamp : ref(4 * float64), source_ip : ref(4 * string)}")

The ampersand is the shorthand for "ref".



Constructors
~~~~~~~~~~~~

Constructors are xnd's way of creating distinct named types. The constructor
argument is a regular type.

Constructors open up a new dtype, so named arrays can be the dtype of
other arrays.  Type inference currently isn't aware of constructors,
so types have to be provided.

.. doctest::

   >>> t = ndt("3 * SomeMatrix(2 * 2 * float32)")
   >>> lst = [[[1,2], [3,4]], [[5,6], [7,8]], [[9,10], [11,12]]]
   >>> x = xnd(lst, type=t)
   >>> x
   xnd([[[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0], [7.0, 8.0]], [[9.0, 10.0], [11.0, 12.0]]],
       type='3 * SomeMatrix(2 * 2 * float32)')
   >>> x[0]
   xnd([[1.0, 2.0], [3.0, 4.0]], type='SomeMatrix(2 * 2 * float32)')


Categorical
~~~~~~~~~~~

Categorical types contain values.  The data stored in xnd buffers are indices
(:c:macro:`int64`) into the type's categories.

.. doctest::

   >>> t = ndt("categorical('a', 'b', 'c', NA)")
   >>> data = ['a', 'a', 'b', 'a', 'a', 'a', 'foo', 'c']
   >>> x = xnd(data, dtype=t)
   >>> x.value
   ['a', 'a', 'b', 'a', 'a', 'a', None, 'c']


Fixed String
~~~~~~~~~~~~

Fixed strings are embedded into arrays.  Supported encodings are 'ascii',
'utf8', 'utf16' and 'utf32'. The string size argument denotes the number
of code points rather than bytes.

.. doctest::

   >>> t = ndt("10 * fixed_string(3, 'utf32')")
   >>> x = xnd.empty(t)
   >>> x.value
   ['', '', '', '', '', '', '', '', '', '']
   >>> x[3] = "\U000003B1\U000003B2\U000003B3"
   >>> x.value
   ['', '', '', 'αβγ', '', '', '', '', '', '']


Fixed Bytes
~~~~~~~~~~~

Fixed bytes are embedded into arrays.

.. doctest::

   >>> t = ndt("3 * fixed_bytes(size=3)")
   >>> x = xnd.empty(t)
   >>> x[2] = b'123'
   >>> x.value
   [b'\x00\x00\x00', b'\x00\x00\x00', b'123']
   >>> x.align
   1

Alignment can be requested with the requirement that size is a multiple of
alignment:

.. doctest::

   >>> t = ndt("3 * fixed_bytes(size=32, align=16)")
   >>> x = xnd.empty(t)
   >>> x.align
   16


String
~~~~~~

Strings are pointers to :c:macro:`NUL`-terminated UTF-8 strings.

.. doctest::

   >>> x = xnd.empty("10 * string")
   >>> x.value
   ['', '', '', '', '', '', '', '', '', '']
   >>> x[0] = "abc"
   >>> x.value
   ['abc', '', '', '', '', '', '', '', '', '']



Bytes
~~~~~

Internally, bytes are structs with a size field and a pointer to the data.

.. doctest::

   >>> xnd([b'123', b'45678'])
   xnd([b'123', b'45678'], type='2 * bytes')


The bytes constructor takes an optional *align* argument that specifies the
alignment of the allocated data:

.. doctest::

   >>> x = xnd([b'abc', b'123'], type="2 * bytes(align=64)")
   >>> x.value
   [b'abc', b'123']
   >>> x.align
   8

Note that *x.align* is the alignment of the array.  The embedded pointers
to the bytes data are aligned at *64*.


Primitive types
~~~~~~~~~~~~~~~

As a short example, here is a tuple that contains all primitive types:

.. doctest::

   >>> s = """
   ...    (bool,
   ...     int8, int16, int32, int64,
   ...     uint8, uint16, uint32, uint64,
   ...     float16, float32, float64,
   ...     complex32, complex64, complex128)
   ... """
   >>> x = xnd.empty(s)
   >>> x.value
   (False, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0j, 0j, 0j)
