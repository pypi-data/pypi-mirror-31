# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.12
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkTransformFileReaderPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_itkTransformFileReaderPython')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_itkTransformFileReaderPython')
    _itkTransformFileReaderPython = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkTransformFileReaderPython', [dirname(__file__)])
        except ImportError:
            import _itkTransformFileReaderPython
            return _itkTransformFileReaderPython
        try:
            _mod = imp.load_module('_itkTransformFileReaderPython', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _itkTransformFileReaderPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkTransformFileReaderPython
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


import itkTransformBasePython
import itkArray2DPython
import vnl_matrixPython
import vnl_vectorPython
import stdcomplexPython
import pyBasePython
import itkVectorPython
import vnl_vector_refPython
import itkFixedArrayPython
import itkArrayPython
import ITKCommonBasePython
import itkVariableLengthVectorPython
import itkOptimizerParametersPython
import itkPointPython
import itkDiffusionTensor3DPython
import itkSymmetricSecondRankTensorPython
import itkMatrixPython
import vnl_matrix_fixedPython
import itkCovariantVectorPython
import itkTransformIOBaseTemplatePython

def itkTransformFileReaderTemplateF_New():
  return itkTransformFileReaderTemplateF.New()

class itkTransformFileReaderTemplateF(ITKCommonBasePython.itkLightProcessObject):
    """Proxy of C++ itkTransformFileReaderTemplateF class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkTransformFileReaderTemplateF_Pointer":
        """__New_orig__() -> itkTransformFileReaderTemplateF_Pointer"""
        return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkTransformFileReaderTemplateF_Pointer":
        """Clone(itkTransformFileReaderTemplateF self) -> itkTransformFileReaderTemplateF_Pointer"""
        return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF_Clone(self)


    def SetFileName(self, *args) -> "void":
        """
        SetFileName(itkTransformFileReaderTemplateF self, char const * _arg)
        SetFileName(itkTransformFileReaderTemplateF self, std::string const & _arg)
        """
        return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF_SetFileName(self, *args)


    def GetFileName(self) -> "char const *":
        """GetFileName(itkTransformFileReaderTemplateF self) -> char const *"""
        return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF_GetFileName(self)


    def Update(self) -> "void":
        """Update(itkTransformFileReaderTemplateF self)"""
        return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF_Update(self)


    def GetTransformList(self) -> "std::list< itkTransformBaseTemplateF_Pointer,std::allocator< itkTransformBaseTemplateF_Pointer > > *":
        """GetTransformList(itkTransformFileReaderTemplateF self) -> std::list< itkTransformBaseTemplateF_Pointer,std::allocator< itkTransformBaseTemplateF_Pointer > > *"""
        return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF_GetTransformList(self)


    def GetModifiableTransformList(self) -> "std::list< itkTransformBaseTemplateF_Pointer,std::allocator< itkTransformBaseTemplateF_Pointer > > *":
        """GetModifiableTransformList(itkTransformFileReaderTemplateF self) -> std::list< itkTransformBaseTemplateF_Pointer,std::allocator< itkTransformBaseTemplateF_Pointer > > *"""
        return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF_GetModifiableTransformList(self)


    def SetTransformIO(self, _arg: 'itkTransformIOBaseTemplateF') -> "void":
        """SetTransformIO(itkTransformFileReaderTemplateF self, itkTransformIOBaseTemplateF _arg)"""
        return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF_SetTransformIO(self, _arg)


    def GetTransformIO(self) -> "itkTransformIOBaseTemplateF const *":
        """GetTransformIO(itkTransformFileReaderTemplateF self) -> itkTransformIOBaseTemplateF"""
        return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF_GetTransformIO(self)

    __swig_destroy__ = _itkTransformFileReaderPython.delete_itkTransformFileReaderTemplateF

    def cast(obj: 'itkLightObject') -> "itkTransformFileReaderTemplateF *":
        """cast(itkLightObject obj) -> itkTransformFileReaderTemplateF"""
        return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self) -> "itkTransformFileReaderTemplateF *":
        """GetPointer(itkTransformFileReaderTemplateF self) -> itkTransformFileReaderTemplateF"""
        return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkTransformFileReaderTemplateF

        Create a new object of the class itkTransformFileReaderTemplateF and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkTransformFileReaderTemplateF.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkTransformFileReaderTemplateF.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkTransformFileReaderTemplateF.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkTransformFileReaderTemplateF.Clone = new_instancemethod(_itkTransformFileReaderPython.itkTransformFileReaderTemplateF_Clone, None, itkTransformFileReaderTemplateF)
itkTransformFileReaderTemplateF.SetFileName = new_instancemethod(_itkTransformFileReaderPython.itkTransformFileReaderTemplateF_SetFileName, None, itkTransformFileReaderTemplateF)
itkTransformFileReaderTemplateF.GetFileName = new_instancemethod(_itkTransformFileReaderPython.itkTransformFileReaderTemplateF_GetFileName, None, itkTransformFileReaderTemplateF)
itkTransformFileReaderTemplateF.Update = new_instancemethod(_itkTransformFileReaderPython.itkTransformFileReaderTemplateF_Update, None, itkTransformFileReaderTemplateF)
itkTransformFileReaderTemplateF.GetTransformList = new_instancemethod(_itkTransformFileReaderPython.itkTransformFileReaderTemplateF_GetTransformList, None, itkTransformFileReaderTemplateF)
itkTransformFileReaderTemplateF.GetModifiableTransformList = new_instancemethod(_itkTransformFileReaderPython.itkTransformFileReaderTemplateF_GetModifiableTransformList, None, itkTransformFileReaderTemplateF)
itkTransformFileReaderTemplateF.SetTransformIO = new_instancemethod(_itkTransformFileReaderPython.itkTransformFileReaderTemplateF_SetTransformIO, None, itkTransformFileReaderTemplateF)
itkTransformFileReaderTemplateF.GetTransformIO = new_instancemethod(_itkTransformFileReaderPython.itkTransformFileReaderTemplateF_GetTransformIO, None, itkTransformFileReaderTemplateF)
itkTransformFileReaderTemplateF.GetPointer = new_instancemethod(_itkTransformFileReaderPython.itkTransformFileReaderTemplateF_GetPointer, None, itkTransformFileReaderTemplateF)
itkTransformFileReaderTemplateF_swigregister = _itkTransformFileReaderPython.itkTransformFileReaderTemplateF_swigregister
itkTransformFileReaderTemplateF_swigregister(itkTransformFileReaderTemplateF)

def itkTransformFileReaderTemplateF___New_orig__() -> "itkTransformFileReaderTemplateF_Pointer":
    """itkTransformFileReaderTemplateF___New_orig__() -> itkTransformFileReaderTemplateF_Pointer"""
    return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF___New_orig__()

def itkTransformFileReaderTemplateF_cast(obj: 'itkLightObject') -> "itkTransformFileReaderTemplateF *":
    """itkTransformFileReaderTemplateF_cast(itkLightObject obj) -> itkTransformFileReaderTemplateF"""
    return _itkTransformFileReaderPython.itkTransformFileReaderTemplateF_cast(obj)



