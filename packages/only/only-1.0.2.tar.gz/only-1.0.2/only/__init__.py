#!/usr/bin/env python
import sys
from decorator import decorator
from objectname import objectname
from public import public

# sys.platform
# linux,linux2,win32,cygwin,darwin


def _raise_OSError(f, msg):
    raise OSError("%s %s" % (objectname(f, fullname=True), msg))


@decorator
@public
def linux(f, *args, **kw):
    if "linux" not in sys.platform:  # linux, linux2
        _raise_OSError(f, "is Linux only :(")
    return f(*args, **kw)


@decorator
@public
def osx(f, *args, **kw):
    if "darwin" not in sys.platform:
        _raise_OSError(f, "is OS X only :(")
    return f(*args, **kw)


@decorator
@public
def unix(f, *args, **kw):
    if "darwin" not in sys.platform and "linux" not in sys.platform:
        _raise_OSError(f, "is Unix only :(")
    return f(*args, **kw)


@decorator
@public
def windows(f, *args, **kw):
    if "win" not in sys.platform:  # win32
        _raise_OSError(f, "is Windows only :(")
    return f(*args, **kw)
