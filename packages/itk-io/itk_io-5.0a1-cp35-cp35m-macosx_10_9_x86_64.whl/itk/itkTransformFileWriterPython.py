# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.12
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkTransformFileWriterPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_itkTransformFileWriterPython')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_itkTransformFileWriterPython')
    _itkTransformFileWriterPython = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkTransformFileWriterPython', [dirname(__file__)])
        except ImportError:
            import _itkTransformFileWriterPython
            return _itkTransformFileWriterPython
        try:
            _mod = imp.load_module('_itkTransformFileWriterPython', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _itkTransformFileWriterPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkTransformFileWriterPython
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


import itkTransformIOBaseTemplatePython
import ITKCommonBasePython
import pyBasePython
import itkTransformBasePython
import itkOptimizerParametersPython
import vnl_vectorPython
import vnl_matrixPython
import stdcomplexPython
import itkArrayPython
import itkVariableLengthVectorPython
import itkCovariantVectorPython
import vnl_vector_refPython
import itkVectorPython
import itkFixedArrayPython
import itkArray2DPython
import itkDiffusionTensor3DPython
import itkSymmetricSecondRankTensorPython
import itkMatrixPython
import itkPointPython
import vnl_matrix_fixedPython

def itkTransformFileWriterTemplateF_New():
  return itkTransformFileWriterTemplateF.New()

class itkTransformFileWriterTemplateF(ITKCommonBasePython.itkLightProcessObject):
    """Proxy of C++ itkTransformFileWriterTemplateF class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkTransformFileWriterTemplateF_Pointer":
        """__New_orig__() -> itkTransformFileWriterTemplateF_Pointer"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkTransformFileWriterTemplateF_Pointer":
        """Clone(itkTransformFileWriterTemplateF self) -> itkTransformFileWriterTemplateF_Pointer"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_Clone(self)


    def SetFileName(self, *args) -> "void":
        """
        SetFileName(itkTransformFileWriterTemplateF self, char const * _arg)
        SetFileName(itkTransformFileWriterTemplateF self, std::string const & _arg)
        """
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_SetFileName(self, *args)


    def GetFileName(self) -> "char const *":
        """GetFileName(itkTransformFileWriterTemplateF self) -> char const *"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_GetFileName(self)


    def SetAppendOff(self) -> "void":
        """SetAppendOff(itkTransformFileWriterTemplateF self)"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_SetAppendOff(self)


    def SetAppendOn(self) -> "void":
        """SetAppendOn(itkTransformFileWriterTemplateF self)"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_SetAppendOn(self)


    def SetAppendMode(self, mode: 'bool') -> "void":
        """SetAppendMode(itkTransformFileWriterTemplateF self, bool mode)"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_SetAppendMode(self, mode)


    def GetAppendMode(self) -> "bool":
        """GetAppendMode(itkTransformFileWriterTemplateF self) -> bool"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_GetAppendMode(self)


    def SetInput(self, transform: 'itkObject') -> "void":
        """SetInput(itkTransformFileWriterTemplateF self, itkObject transform)"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_SetInput(self, transform)


    def GetInput(self) -> "itkTransformBaseTemplateF const *":
        """GetInput(itkTransformFileWriterTemplateF self) -> itkTransformBaseTemplateF"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_GetInput(self)


    def AddTransform(self, transform: 'itkObject') -> "void":
        """AddTransform(itkTransformFileWriterTemplateF self, itkObject transform)"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_AddTransform(self, transform)


    def Update(self) -> "void":
        """Update(itkTransformFileWriterTemplateF self)"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_Update(self)


    def SetTransformIO(self, _arg: 'itkTransformIOBaseTemplateF') -> "void":
        """SetTransformIO(itkTransformFileWriterTemplateF self, itkTransformIOBaseTemplateF _arg)"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_SetTransformIO(self, _arg)


    def GetTransformIO(self) -> "itkTransformIOBaseTemplateF const *":
        """GetTransformIO(itkTransformFileWriterTemplateF self) -> itkTransformIOBaseTemplateF"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_GetTransformIO(self)

    __swig_destroy__ = _itkTransformFileWriterPython.delete_itkTransformFileWriterTemplateF

    def cast(obj: 'itkLightObject') -> "itkTransformFileWriterTemplateF *":
        """cast(itkLightObject obj) -> itkTransformFileWriterTemplateF"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_cast(obj)

    cast = staticmethod(cast)

    def GetPointer(self) -> "itkTransformFileWriterTemplateF *":
        """GetPointer(itkTransformFileWriterTemplateF self) -> itkTransformFileWriterTemplateF"""
        return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_GetPointer(self)


    def New(*args, **kargs):
        """New() -> itkTransformFileWriterTemplateF

        Create a new object of the class itkTransformFileWriterTemplateF and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkTransformFileWriterTemplateF.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkTransformFileWriterTemplateF.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkTransformFileWriterTemplateF.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkTransformFileWriterTemplateF.Clone = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_Clone, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.SetFileName = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_SetFileName, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.GetFileName = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_GetFileName, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.SetAppendOff = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_SetAppendOff, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.SetAppendOn = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_SetAppendOn, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.SetAppendMode = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_SetAppendMode, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.GetAppendMode = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_GetAppendMode, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.SetInput = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_SetInput, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.GetInput = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_GetInput, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.AddTransform = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_AddTransform, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.Update = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_Update, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.SetTransformIO = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_SetTransformIO, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.GetTransformIO = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_GetTransformIO, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF.GetPointer = new_instancemethod(_itkTransformFileWriterPython.itkTransformFileWriterTemplateF_GetPointer, None, itkTransformFileWriterTemplateF)
itkTransformFileWriterTemplateF_swigregister = _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_swigregister
itkTransformFileWriterTemplateF_swigregister(itkTransformFileWriterTemplateF)

def itkTransformFileWriterTemplateF___New_orig__() -> "itkTransformFileWriterTemplateF_Pointer":
    """itkTransformFileWriterTemplateF___New_orig__() -> itkTransformFileWriterTemplateF_Pointer"""
    return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF___New_orig__()

def itkTransformFileWriterTemplateF_cast(obj: 'itkLightObject') -> "itkTransformFileWriterTemplateF *":
    """itkTransformFileWriterTemplateF_cast(itkLightObject obj) -> itkTransformFileWriterTemplateF"""
    return _itkTransformFileWriterPython.itkTransformFileWriterTemplateF_cast(obj)



