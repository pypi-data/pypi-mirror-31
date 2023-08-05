# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.12
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkLSMImageIOPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_itkLSMImageIOPython')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_itkLSMImageIOPython')
    _itkLSMImageIOPython = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkLSMImageIOPython', [dirname(__file__)])
        except ImportError:
            import _itkLSMImageIOPython
            return _itkLSMImageIOPython
        try:
            _mod = imp.load_module('_itkLSMImageIOPython', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _itkLSMImageIOPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkLSMImageIOPython
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


import itkTIFFImageIOPython
import itkRGBPixelPython
import itkFixedArrayPython
import pyBasePython
import ITKCommonBasePython
import ITKIOImageBaseBasePython
import vnl_vectorPython
import vnl_matrixPython
import stdcomplexPython

def itkLSMImageIOFactory_New():
  return itkLSMImageIOFactory.New()


def itkLSMImageIO_New():
  return itkLSMImageIO.New()

class itkLSMImageIO(itkTIFFImageIOPython.itkTIFFImageIO):
    """


    ImageIO class for reading LSM (Zeiss) images LSM is a line of confocal
    laser scanning microscopes produced by the Zeiss company LSM files are
    essentially extensions of the TIFF multiple image stack file format.

    C++ includes: itkLSMImageIO.h 
    """

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkLSMImageIO_Pointer":
        """__New_orig__() -> itkLSMImageIO_Pointer"""
        return _itkLSMImageIOPython.itkLSMImageIO___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkLSMImageIO_Pointer":
        """Clone(itkLSMImageIO self) -> itkLSMImageIO_Pointer"""
        return _itkLSMImageIOPython.itkLSMImageIO_Clone(self)

    __swig_destroy__ = _itkLSMImageIOPython.delete_itkLSMImageIO

    def cast(obj: 'itkLightObject') -> "itkLSMImageIO *":
        """cast(itkLightObject obj) -> itkLSMImageIO"""
        return _itkLSMImageIOPython.itkLSMImageIO_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self) -> "itkLSMImageIO *":
        """GetPointer(itkLSMImageIO self) -> itkLSMImageIO"""
        return _itkLSMImageIOPython.itkLSMImageIO_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkLSMImageIO

        Create a new object of the class itkLSMImageIO and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkLSMImageIO.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkLSMImageIO.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkLSMImageIO.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkLSMImageIO.Clone = new_instancemethod(_itkLSMImageIOPython.itkLSMImageIO_Clone, None, itkLSMImageIO)
itkLSMImageIO.GetPointer = new_instancemethod(_itkLSMImageIOPython.itkLSMImageIO_GetPointer, None, itkLSMImageIO)
itkLSMImageIO_swigregister = _itkLSMImageIOPython.itkLSMImageIO_swigregister
itkLSMImageIO_swigregister(itkLSMImageIO)

def itkLSMImageIO___New_orig__() -> "itkLSMImageIO_Pointer":
    """itkLSMImageIO___New_orig__() -> itkLSMImageIO_Pointer"""
    return _itkLSMImageIOPython.itkLSMImageIO___New_orig__()

def itkLSMImageIO_cast(obj: 'itkLightObject') -> "itkLSMImageIO *":
    """itkLSMImageIO_cast(itkLightObject obj) -> itkLSMImageIO"""
    return _itkLSMImageIOPython.itkLSMImageIO_cast(obj)

class itkLSMImageIOFactory(ITKCommonBasePython.itkObjectFactoryBase):
    """


    Create instances of LSMImageIO objects using an object factory.

    C++ includes: itkLSMImageIOFactory.h 
    """

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkLSMImageIOFactory_Pointer":
        """__New_orig__() -> itkLSMImageIOFactory_Pointer"""
        return _itkLSMImageIOPython.itkLSMImageIOFactory___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def RegisterOneFactory() -> "void":
        """RegisterOneFactory()"""
        return _itkLSMImageIOPython.itkLSMImageIOFactory_RegisterOneFactory()

    RegisterOneFactory = staticmethod(RegisterOneFactory)
    __swig_destroy__ = _itkLSMImageIOPython.delete_itkLSMImageIOFactory

    def cast(obj: 'itkLightObject') -> "itkLSMImageIOFactory *":
        """cast(itkLightObject obj) -> itkLSMImageIOFactory"""
        return _itkLSMImageIOPython.itkLSMImageIOFactory_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self) -> "itkLSMImageIOFactory *":
        """GetPointer(itkLSMImageIOFactory self) -> itkLSMImageIOFactory"""
        return _itkLSMImageIOPython.itkLSMImageIOFactory_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkLSMImageIOFactory

        Create a new object of the class itkLSMImageIOFactory and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkLSMImageIOFactory.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkLSMImageIOFactory.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkLSMImageIOFactory.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkLSMImageIOFactory.GetPointer = new_instancemethod(_itkLSMImageIOPython.itkLSMImageIOFactory_GetPointer, None, itkLSMImageIOFactory)
itkLSMImageIOFactory_swigregister = _itkLSMImageIOPython.itkLSMImageIOFactory_swigregister
itkLSMImageIOFactory_swigregister(itkLSMImageIOFactory)

def itkLSMImageIOFactory___New_orig__() -> "itkLSMImageIOFactory_Pointer":
    """itkLSMImageIOFactory___New_orig__() -> itkLSMImageIOFactory_Pointer"""
    return _itkLSMImageIOPython.itkLSMImageIOFactory___New_orig__()

def itkLSMImageIOFactory_RegisterOneFactory() -> "void":
    """itkLSMImageIOFactory_RegisterOneFactory()"""
    return _itkLSMImageIOPython.itkLSMImageIOFactory_RegisterOneFactory()

def itkLSMImageIOFactory_cast(obj: 'itkLightObject') -> "itkLSMImageIOFactory *":
    """itkLSMImageIOFactory_cast(itkLightObject obj) -> itkLSMImageIOFactory"""
    return _itkLSMImageIOPython.itkLSMImageIOFactory_cast(obj)



