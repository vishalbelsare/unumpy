"""
.. note:
    If you are looking for overrides for NumPy-specific methods, see the
    documentation for :obj:`unumpy`. This page explains how to write
    back-ends and multimethods.

``uarray`` is built around a back-end protocol, and overridable multimethods.
It is necessary to define multimethods for back-ends to be able to override them.
See the documentation of :obj:`generate_multimethod` on how to write multimethods.



Let's start with the simplest:

``__ua_domain__`` defines the back-end *domain*. The domain consists of a string
that, by convention, is the module for which a back-end is provided, along with
related packages in the ecosystem. For example, the ``"numpy"`` domain may cover
backends for NumPy itself, as well as SciPy and the numerical scikit packages.

For the purpose of this demonstration, we'll be creating an object and setting
its attributes directly. However, note that you can use a module or your own type
as a backend as well.

>>> class Backend: pass
>>> be = Backend()
>>> be.__ua_domain__ = "ua_examples"

It might be useful at this point to sidetrack to the documentation of
:obj:`generate_multimethod` to find out how to generate a multimethod
overridable by :obj:`uarray`. Needless to say, writing a backend and
creating multimethods are mostly orthogonal activities, and knowing
one doesn't necessarily require knowledge of the other, although it
is certainly helpful. We expect core API designers/specifiers to write the
multimethods, and implementors to override them. But, as is often the case,
similar people write both.

Without further ado, here's an example multimethTrueod:

>>> import uarray as ua
>>> def override_me(a, b):
...   return Dispatchable(a, int),
>>> def override_replacer(args, kwargs, dispatchables):
...     return (dispatchables[0], args[1]), {}
>>> overridden_me = ua.generate_multimethod(
...     override_me, override_replacer, "ua_examples"
... )

Next comes the part about overriding the multimethod. This requires
the ``__ua_function__`` protocol, and the ``__ua_convert__``
protocol. The ``__ua_function__`` protocol has the signature
``(method, args, kwargs, dispatchables)`` where ``method`` is the passed
multimethod, ``args``/``kwargs`` specify the arguments and ``dispatchables``
is the list of converted dispatchables passed in.

>>> def __ua_function__(method, args, kwargs, dispatchables):
...     return method.__name__, args, kwargs, dispatchables
>>> be.__ua_function__ = __ua_function__

The other protocol of interest is the ``__ua_convert__`` protocol. It has the
signature ``(arg, type, coerce)``. When ``coerce`` is ``False``, conversion between
the formats should ideally be an ``O(1)`` operation.

>>> def __ua_convert__(value, type, coerce):
...     if type is int:
...         if not coerce:
...             return value
...         return str(value)
...     return NotImplemented
>>> be.__ua_convert__ = __ua_convert__

Now that we have defined the backend, the next thing to do is to call the multimethod.

>>> with ua.set_backend(be):
...      overridden_me(1, "2")
('override_me', (1, '2'), {}, [<Dispatchable: type=<class 'int'>, value=1>])

Note that the marked type has no effect on the actual type of the passed object.
We can also coerce the type of the input.

>>> with ua.set_backend(be, coerce=True):
...     overridden_me(1, "2")
...     overridden_me(1.0, "2")
('override_me', ('1', '2'), {}, [<Dispatchable: type=<class 'int'>, value='1'>])
('override_me', ('1.0', '2'), {}, [<Dispatchable: type=<class 'int'>, value='1.0'>])

Another feature is that if you return ``NotImplemented`` from ``__ua_convert__``,
it doesn't get passed into the ``dispatchables`` arg.

>>> def __ua_convert__(value, type, coerce):
...     return NotImplemented
>>> be.__ua_convert__ = __ua_convert__
>>> with ua.set_backend(be):
...     overridden_me(1, "2")
('override_me', (1, '2'), {}, [])

You also have the option to return ``NotImplemented``, in which case processing moves on
to the next back-end, which in this case, doesn't exist.

Notice that for classes, a :obj:`Dispatchable` instance is guaranteed to be passed in.

>>> be.__ua_function__ = lambda *a, **kw: NotImplemented
>>> with ua.set_backend(be):
...     overridden_me(1, "2")
Traceback (most recent call last):
    ...
uarray.backend.BackendNotImplementedError: ...

The last possibility is if we don't have ``__ua_convert__``, in which case the job is left
up to ``__ua_function__``, but putting things back into arrays after conversion will not be
possible.
"""

import uarray.backend as backend
from .backend import *
from ._version import get_versions  # type: ignore

__version__ = get_versions()["version"]
del get_versions
