# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.12
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkGE4ImageIOPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_itkGE4ImageIOPython')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_itkGE4ImageIOPython')
    _itkGE4ImageIOPython = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkGE4ImageIOPython', [dirname(__file__)])
        except ImportError:
            import _itkGE4ImageIOPython
            return _itkGE4ImageIOPython
        try:
            _mod = imp.load_module('_itkGE4ImageIOPython', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _itkGE4ImageIOPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkGE4ImageIOPython
del _swig_python_version_info

try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        object.__setattr__(self, name, value)
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    raise AttributeError("'%s' object has no attribute '%s'" % (class_type.__name__, name))


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)


def _swig_setattr_nondynamic_method(set):
    def set_attr(self, name, value):
        if (name == "thisown"):
            return self.this.own(value)
        if hasattr(self, name) or (name == "this"):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add attributes to %s" % self)
    return set_attr


import itkIPLCommonImageIOPython
import ITKCommonBasePython
import pyBasePython
import ITKIOImageBaseBasePython
import vnl_vectorPython
import vnl_matrixPython
import stdcomplexPython

def itkGE4ImageIOFactory_New():
  return itkGE4ImageIOFactory.New()


def itkGE4ImageIO_New():
  return itkGE4ImageIO.New()

class itkGE4ImageIO(itkIPLCommonImageIOPython.itkIPLCommonImageIO):
    """


    Class that defines how to read GE4 file format.

    Hans J. Johnson

    C++ includes: itkGE4ImageIO.h 
    """

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkGE4ImageIO_Pointer":
        """__New_orig__() -> itkGE4ImageIO_Pointer"""
        return _itkGE4ImageIOPython.itkGE4ImageIO___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkGE4ImageIO_Pointer":
        """Clone(itkGE4ImageIO self) -> itkGE4ImageIO_Pointer"""
        return _itkGE4ImageIOPython.itkGE4ImageIO_Clone(self)

    __swig_destroy__ = _itkGE4ImageIOPython.delete_itkGE4ImageIO

    def cast(obj: 'itkLightObject') -> "itkGE4ImageIO *":
        """cast(itkLightObject obj) -> itkGE4ImageIO"""
        return _itkGE4ImageIOPython.itkGE4ImageIO_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self) -> "itkGE4ImageIO *":
        """GetPointer(itkGE4ImageIO self) -> itkGE4ImageIO"""
        return _itkGE4ImageIOPython.itkGE4ImageIO_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkGE4ImageIO

        Create a new object of the class itkGE4ImageIO and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkGE4ImageIO.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkGE4ImageIO.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkGE4ImageIO.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkGE4ImageIO.Clone = new_instancemethod(_itkGE4ImageIOPython.itkGE4ImageIO_Clone, None, itkGE4ImageIO)
itkGE4ImageIO.GetPointer = new_instancemethod(_itkGE4ImageIOPython.itkGE4ImageIO_GetPointer, None, itkGE4ImageIO)
itkGE4ImageIO_swigregister = _itkGE4ImageIOPython.itkGE4ImageIO_swigregister
itkGE4ImageIO_swigregister(itkGE4ImageIO)

def itkGE4ImageIO___New_orig__() -> "itkGE4ImageIO_Pointer":
    """itkGE4ImageIO___New_orig__() -> itkGE4ImageIO_Pointer"""
    return _itkGE4ImageIOPython.itkGE4ImageIO___New_orig__()

def itkGE4ImageIO_cast(obj: 'itkLightObject') -> "itkGE4ImageIO *":
    """itkGE4ImageIO_cast(itkLightObject obj) -> itkGE4ImageIO"""
    return _itkGE4ImageIOPython.itkGE4ImageIO_cast(obj)

class itkGE4ImageIOFactory(ITKCommonBasePython.itkObjectFactoryBase):
    """


    Create instances of GE4ImageIO objects using an object factory.

    C++ includes: itkGE4ImageIOFactory.h 
    """

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkGE4ImageIOFactory_Pointer":
        """__New_orig__() -> itkGE4ImageIOFactory_Pointer"""
        return _itkGE4ImageIOPython.itkGE4ImageIOFactory___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def RegisterOneFactory() -> "void":
        """RegisterOneFactory()"""
        return _itkGE4ImageIOPython.itkGE4ImageIOFactory_RegisterOneFactory()

    RegisterOneFactory = staticmethod(RegisterOneFactory)
    __swig_destroy__ = _itkGE4ImageIOPython.delete_itkGE4ImageIOFactory

    def cast(obj: 'itkLightObject') -> "itkGE4ImageIOFactory *":
        """cast(itkLightObject obj) -> itkGE4ImageIOFactory"""
        return _itkGE4ImageIOPython.itkGE4ImageIOFactory_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self) -> "itkGE4ImageIOFactory *":
        """GetPointer(itkGE4ImageIOFactory self) -> itkGE4ImageIOFactory"""
        return _itkGE4ImageIOPython.itkGE4ImageIOFactory_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkGE4ImageIOFactory

        Create a new object of the class itkGE4ImageIOFactory and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkGE4ImageIOFactory.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkGE4ImageIOFactory.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkGE4ImageIOFactory.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkGE4ImageIOFactory.GetPointer = new_instancemethod(_itkGE4ImageIOPython.itkGE4ImageIOFactory_GetPointer, None, itkGE4ImageIOFactory)
itkGE4ImageIOFactory_swigregister = _itkGE4ImageIOPython.itkGE4ImageIOFactory_swigregister
itkGE4ImageIOFactory_swigregister(itkGE4ImageIOFactory)

def itkGE4ImageIOFactory___New_orig__() -> "itkGE4ImageIOFactory_Pointer":
    """itkGE4ImageIOFactory___New_orig__() -> itkGE4ImageIOFactory_Pointer"""
    return _itkGE4ImageIOPython.itkGE4ImageIOFactory___New_orig__()

def itkGE4ImageIOFactory_RegisterOneFactory() -> "void":
    """itkGE4ImageIOFactory_RegisterOneFactory()"""
    return _itkGE4ImageIOPython.itkGE4ImageIOFactory_RegisterOneFactory()

def itkGE4ImageIOFactory_cast(obj: 'itkLightObject') -> "itkGE4ImageIOFactory *":
    """itkGE4ImageIOFactory_cast(itkLightObject obj) -> itkGE4ImageIOFactory"""
    return _itkGE4ImageIOPython.itkGE4ImageIOFactory_cast(obj)



