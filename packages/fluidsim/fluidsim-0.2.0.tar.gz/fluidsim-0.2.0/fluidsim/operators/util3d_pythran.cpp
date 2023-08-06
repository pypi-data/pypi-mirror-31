#define BOOST_SIMD_NO_STRICT_ALIASING 1
#include <pythonic/core.hpp>
#include <pythonic/python/core.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/int.hpp>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <pythonic/include/types/float64.hpp>
#include <pythonic/include/types/complex128.hpp>
#include <pythonic/include/types/uint8.hpp>
#include <pythonic/include/types/ndarray.hpp>
#include <pythonic/include/types/int.hpp>
#include <pythonic/types/uint8.hpp>
#include <pythonic/types/complex128.hpp>
#include <pythonic/types/float64.hpp>
#include <pythonic/types/int.hpp>
#include <pythonic/types/ndarray.hpp>
#include <pythonic/include/types/complex.hpp>
#include <pythonic/include/__builtin__/None.hpp>
#include <pythonic/include/__builtin__/tuple.hpp>
#include <pythonic/include/types/str.hpp>
#include <pythonic/include/operator_/div.hpp>
#include <pythonic/include/__builtin__/range.hpp>
#include <pythonic/include/operator_/idiv.hpp>
#include <pythonic/include/__builtin__/getattr.hpp>
#include <pythonic/include/numpy/square.hpp>
#include <pythonic/types/complex.hpp>
#include <pythonic/__builtin__/None.hpp>
#include <pythonic/__builtin__/tuple.hpp>
#include <pythonic/types/str.hpp>
#include <pythonic/operator_/div.hpp>
#include <pythonic/__builtin__/range.hpp>
#include <pythonic/operator_/idiv.hpp>
#include <pythonic/__builtin__/getattr.hpp>
#include <pythonic/numpy/square.hpp>
namespace __pythran_util3d_pythran
{
  struct urudfft_from_vxvyfft
  {
    typedef void callable;
    typedef void pure;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type0;
      typedef std::complex<double> __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type2;
      typedef decltype((std::declval<__type2>() * std::declval<__type0>())) __type3;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type4;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type5;
      typedef decltype((std::declval<__type4>() * std::declval<__type5>())) __type6;
      typedef decltype((std::declval<__type3>() + std::declval<__type6>())) __type7;
      typedef typename pythonic::assignable<decltype((std::declval<__type1>() * std::declval<__type7>()))>::type __type8;
      typedef decltype((std::declval<__type8>() * std::declval<__type2>())) __type9;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::square{})>::type>::type __type10;
      typedef decltype(std::declval<__type10>()(std::declval<__type2>())) __type11;
      typedef decltype(std::declval<__type10>()(std::declval<__type4>())) __type12;
      typedef typename pythonic::assignable<decltype((std::declval<__type11>() + std::declval<__type12>()))>::type __type13;
      typedef double __type14;
      typedef container<typename std::remove_reference<__type14>::type> __type15;
      typedef typename __combined<__type13,__type15>::type __type16;
      typedef decltype((std::declval<__type16>() == std::declval<__type14>())) __type17;
      typedef indexable<__type17> __type18;
      typedef typename __combined<__type13,__type18>::type __type19;
      typedef typename __combined<__type19,__type15>::type __type20;
      typedef typename __combined<__type20,__type18>::type __type21;
      typedef typename __combined<__type21,__type15>::type __type22;
      typedef decltype((pythonic::operator_::div(std::declval<__type9>(), std::declval<__type22>()))) __type23;
      typedef typename pythonic::assignable<decltype((std::declval<__type0>() - std::declval<__type23>()))>::type __type24;
      typedef decltype((std::declval<__type8>() * std::declval<__type4>())) __type25;
      typedef decltype((pythonic::operator_::div(std::declval<__type25>(), std::declval<__type22>()))) __type26;
      typedef typename pythonic::assignable<decltype((std::declval<__type5>() - std::declval<__type26>()))>::type __type27;
      typedef decltype((std::declval<__type0>() - std::declval<__type24>())) __type28;
      typedef decltype((std::declval<__type5>() - std::declval<__type27>())) __type29;
      typedef typename pythonic::returnable<decltype(pythonic::types::make_tuple(std::declval<__type24>(), std::declval<__type27>(), std::declval<__type28>(), std::declval<__type29>()))>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 >
    typename type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4>::result_type operator()(argument_type0&& vx_fft, argument_type1&& vy_fft, argument_type2&& kx, argument_type3&& ky, argument_type4&& rank) const
    ;
  }  ;
  struct dealiasing_variable
  {
    typedef void callable;
    ;
    template <typename argument_type0 , typename argument_type1 >
    struct type
    {
      typedef double __type0;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::range{})>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type2;
      typedef decltype(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(std::declval<__type2>())) __type3;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type3>::type>::type __type4;
      typedef typename pythonic::lazy<__type4>::type __type5;
      typedef decltype(std::declval<__type1>()(std::declval<__type5>())) __type6;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type6>::type::iterator>::value_type>::type __type7;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type3>::type>::type __type8;
      typedef typename pythonic::lazy<__type8>::type __type9;
      typedef decltype(std::declval<__type1>()(std::declval<__type9>())) __type10;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type10>::type::iterator>::value_type>::type __type11;
      typedef typename std::tuple_element<2,typename std::remove_reference<__type3>::type>::type __type12;
      typedef typename pythonic::lazy<__type12>::type __type13;
      typedef decltype(std::declval<__type1>()(std::declval<__type13>())) __type14;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type14>::type::iterator>::value_type>::type __type15;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type7>(), std::declval<__type11>(), std::declval<__type15>())) __type16;
      typedef __type0 __ptype0;
      typedef __type16 __ptype1;
      typedef typename pythonic::returnable<pythonic::types::none_type>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 >
    typename type<argument_type0, argument_type1>::result_type operator()(argument_type0&& ff_fft, argument_type1&& where_dealiased) const
    ;
  }  ;
  struct dealiasing_setofvar
  {
    typedef void callable;
    ;
    template <typename argument_type0 , typename argument_type1 >
    struct type
    {
      typedef double __type0;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::__builtin__::functor::range{})>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type2;
      typedef decltype(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(std::declval<__type2>())) __type3;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type3>::type>::type __type4;
      typedef typename pythonic::lazy<__type4>::type __type5;
      typedef decltype(std::declval<__type1>()(std::declval<__type5>())) __type6;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type6>::type::iterator>::value_type>::type __type7;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type3>::type>::type __type8;
      typedef typename pythonic::lazy<__type8>::type __type9;
      typedef decltype(std::declval<__type1>()(std::declval<__type9>())) __type10;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type10>::type::iterator>::value_type>::type __type11;
      typedef typename std::tuple_element<2,typename std::remove_reference<__type3>::type>::type __type12;
      typedef typename pythonic::lazy<__type12>::type __type13;
      typedef decltype(std::declval<__type1>()(std::declval<__type13>())) __type14;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type14>::type::iterator>::value_type>::type __type15;
      typedef typename std::tuple_element<3,typename std::remove_reference<__type3>::type>::type __type16;
      typedef typename pythonic::lazy<__type16>::type __type17;
      typedef decltype(std::declval<__type1>()(std::declval<__type17>())) __type18;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type18>::type::iterator>::value_type>::type __type19;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type7>(), std::declval<__type11>(), std::declval<__type15>(), std::declval<__type19>())) __type20;
      typedef __type0 __ptype4;
      typedef __type20 __ptype5;
      typedef typename pythonic::returnable<pythonic::types::none_type>::type result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 >
    typename type<argument_type0, argument_type1>::result_type operator()(argument_type0&& sov, argument_type1&& where_dealiased) const
    ;
  }  ;
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 >
  typename urudfft_from_vxvyfft::type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4>::result_type urudfft_from_vxvyfft::operator()(argument_type0&& vx_fft, argument_type1&& vy_fft, argument_type2&& kx, argument_type3&& ky, argument_type4&& rank) const
  {
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::square{})>::type>::type __type0;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type1;
    typedef decltype(std::declval<__type0>()(std::declval<__type1>())) __type2;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type3;
    typedef decltype(std::declval<__type0>()(std::declval<__type3>())) __type4;
    typedef typename pythonic::assignable<decltype((std::declval<__type2>() + std::declval<__type4>()))>::type __type5;
    typedef double __type6;
    typedef container<typename std::remove_reference<__type6>::type> __type7;
    typedef typename __combined<__type5,__type7>::type __type8;
    typedef decltype((std::declval<__type8>() == std::declval<__type6>())) __type9;
    typedef indexable<__type9> __type10;
    typedef typename __combined<__type5,__type10>::type __type11;
    typedef typename __combined<__type11,__type7>::type __type12;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type13;
    typedef std::complex<double> __type14;
    typedef decltype((std::declval<__type1>() * std::declval<__type13>())) __type15;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type16;
    typedef decltype((std::declval<__type3>() * std::declval<__type16>())) __type17;
    typedef decltype((std::declval<__type15>() + std::declval<__type17>())) __type18;
    typedef typename pythonic::assignable<decltype((std::declval<__type14>() * std::declval<__type18>()))>::type __type19;
    typedef decltype((std::declval<__type19>() * std::declval<__type1>())) __type20;
    typedef typename __combined<__type12,__type10>::type __type21;
    typedef typename __combined<__type21,__type7>::type __type22;
    typedef decltype((pythonic::operator_::div(std::declval<__type20>(), std::declval<__type22>()))) __type23;
    typedef decltype((std::declval<__type19>() * std::declval<__type3>())) __type24;
    typedef decltype((pythonic::operator_::div(std::declval<__type24>(), std::declval<__type22>()))) __type25;
    typename pythonic::assignable<typename __combined<__type12,__type10>::type>::type k2 = (pythonic::numpy::functor::square{}(kx) + pythonic::numpy::functor::square{}(ky));
    k2.fast((k2 == 0.0)) = 1e-10;
    typename pythonic::assignable<decltype((std::complex<double>(0.0, 1.0) * ((kx * vx_fft) + (ky * vy_fft))))>::type divh_fft = (std::complex<double>(0.0, 1.0) * ((kx * vx_fft) + (ky * vy_fft)));
    typename pythonic::assignable<typename pythonic::assignable<decltype((std::declval<__type13>() - std::declval<__type23>()))>::type>::type urx_fft = (vx_fft - (pythonic::operator_::div((divh_fft * kx), k2)));
    typename pythonic::assignable<typename pythonic::assignable<decltype((std::declval<__type16>() - std::declval<__type25>()))>::type>::type ury_fft = (vy_fft - (pythonic::operator_::div((divh_fft * ky), k2)));
    ;
    ;
    return pythonic::types::make_tuple(urx_fft, ury_fft, (vx_fft - urx_fft), (vy_fft - ury_fft));
  }
  template <typename argument_type0 , typename argument_type1 >
  typename dealiasing_variable::type<argument_type0, argument_type1>::result_type dealiasing_variable::operator()(argument_type0&& ff_fft, argument_type1&& where_dealiased) const
  {
    typename pythonic::lazy<decltype(std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(ff_fft)))>::type n0 = std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(ff_fft));
    typename pythonic::lazy<decltype(std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(ff_fft)))>::type n1 = std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(ff_fft));
    typename pythonic::lazy<decltype(std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(ff_fft)))>::type n2 = std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(ff_fft));
    {
      long  __target1 = n0;
      for (long  i0=0L; i0 < __target1; i0 += 1L)
      {
        {
          long  __target2 = n1;
          for (long  i1=0L; i1 < __target2; i1 += 1L)
          {
            {
              long  __target3 = n2;
              for (long  i2=0L; i2 < __target3; i2 += 1L)
              {
                if (where_dealiased.fast(pythonic::types::make_tuple(i0, i1, i2)))
                {
                  ff_fft.fast(pythonic::types::make_tuple(i0, i1, i2)) = 0.0;
                }
              }
            }
          }
        }
      }
    }
    return pythonic::__builtin__::None;
  }
  template <typename argument_type0 , typename argument_type1 >
  typename dealiasing_setofvar::type<argument_type0, argument_type1>::result_type dealiasing_setofvar::operator()(argument_type0&& sov, argument_type1&& where_dealiased) const
  {
    typename pythonic::lazy<decltype(std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(sov)))>::type nk = std::get<0>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(sov));
    typename pythonic::lazy<decltype(std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(sov)))>::type n0 = std::get<1>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(sov));
    typename pythonic::lazy<decltype(std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(sov)))>::type n1 = std::get<2>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(sov));
    typename pythonic::lazy<decltype(std::get<3>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(sov)))>::type n2 = std::get<3>(pythonic::__builtin__::getattr<pythonic::types::attr::SHAPE>(sov));
    {
      long  __target1 = n0;
      for (long  i0=0L; i0 < __target1; i0 += 1L)
      {
        {
          long  __target2 = n1;
          for (long  i1=0L; i1 < __target2; i1 += 1L)
          {
            {
              long  __target3 = n2;
              for (long  i2=0L; i2 < __target3; i2 += 1L)
              {
                if (where_dealiased.fast(pythonic::types::make_tuple(i0, i1, i2)))
                {
                  {
                    long  __target4 = nk;
                    for (long  ik=0L; ik < __target4; ik += 1L)
                    {
                      sov.fast(pythonic::types::make_tuple(ik, i0, i1, i2)) = 0.0;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    return pythonic::__builtin__::None;
  }
}
#include <pythonic/python/exception_handler.hpp>
#ifdef ENABLE_PYTHON_MODULE
typename __pythran_util3d_pythran::urudfft_from_vxvyfft::type<pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<double,3>, pythonic::types::ndarray<double,3>, long>::result_type urudfft_from_vxvyfft0(pythonic::types::ndarray<std::complex<double>,3>&& vx_fft, pythonic::types::ndarray<std::complex<double>,3>&& vy_fft, pythonic::types::ndarray<double,3>&& kx, pythonic::types::ndarray<double,3>&& ky, long&& rank) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util3d_pythran::urudfft_from_vxvyfft()(vx_fft, vy_fft, kx, ky, rank);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util3d_pythran::dealiasing_variable::type<pythonic::types::ndarray<std::complex<double>,3>, pythonic::types::ndarray<uint8_t,3>>::result_type dealiasing_variable0(pythonic::types::ndarray<std::complex<double>,3>&& ff_fft, pythonic::types::ndarray<uint8_t,3>&& where_dealiased) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util3d_pythran::dealiasing_variable()(ff_fft, where_dealiased);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
typename __pythran_util3d_pythran::dealiasing_setofvar::type<pythonic::types::ndarray<std::complex<double>,4>, pythonic::types::ndarray<uint8_t,3>>::result_type dealiasing_setofvar0(pythonic::types::ndarray<std::complex<double>,4>&& sov, pythonic::types::ndarray<uint8_t,3>&& where_dealiased) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_util3d_pythran::dealiasing_setofvar()(sov, where_dealiased);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}

static PyObject *
__pythran_wrap_urudfft_from_vxvyfft0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    char const* keywords[] = {"vx_fft","vy_fft","kx","ky","rank", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords, &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,3>>(args_obj[3]) && is_convertible<long>(args_obj[4]))
        return to_python(urudfft_from_vxvyfft0(from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[1]), from_python<pythonic::types::ndarray<double,3>>(args_obj[2]), from_python<pythonic::types::ndarray<double,3>>(args_obj[3]), from_python<long>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_dealiasing_variable0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    char const* keywords[] = {"ff_fft","where_dealiased", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords, &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<uint8_t,3>>(args_obj[1]))
        return to_python(dealiasing_variable0(from_python<pythonic::types::ndarray<std::complex<double>,3>>(args_obj[0]), from_python<pythonic::types::ndarray<uint8_t,3>>(args_obj[1])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_dealiasing_setofvar0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    char const* keywords[] = {"sov","where_dealiased", nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords, &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,4>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<uint8_t,3>>(args_obj[1]))
        return to_python(dealiasing_setofvar0(from_python<pythonic::types::ndarray<std::complex<double>,4>>(args_obj[0]), from_python<pythonic::types::ndarray<uint8_t,3>>(args_obj[1])));
    else {
        return nullptr;
    }
}

            static PyObject *
            __pythran_wrapall_urudfft_from_vxvyfft(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_urudfft_from_vxvyfft0(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "urudfft_from_vxvyfft", "   urudfft_from_vxvyfft(complex128[][][],complex128[][][],float64[][][],float64[][][],int)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_dealiasing_variable(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_dealiasing_variable0(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "dealiasing_variable", "   dealiasing_variable(complex128[][][],uint8[][][])", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_dealiasing_setofvar(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_dealiasing_setofvar0(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "dealiasing_setofvar", "   dealiasing_setofvar(complex128[][][][],uint8[][][])", args, kw);
                });
            }


static PyMethodDef Methods[] = {
    {
    "urudfft_from_vxvyfft",
    (PyCFunction)__pythran_wrapall_urudfft_from_vxvyfft,
    METH_VARARGS | METH_KEYWORDS,
    "Supported prototypes:\n\n    - urudfft_from_vxvyfft(complex128[][][], complex128[][][], float64[][][], float64[][][], int)"},{
    "dealiasing_variable",
    (PyCFunction)__pythran_wrapall_dealiasing_variable,
    METH_VARARGS | METH_KEYWORDS,
    "Dealiasing 3d array\n\n    Supported prototypes:\n\n    - dealiasing_variable(complex128[][][], uint8[][][])"},{
    "dealiasing_setofvar",
    (PyCFunction)__pythran_wrapall_dealiasing_setofvar,
    METH_VARARGS | METH_KEYWORDS,
    "Dealiasing 3d setofvar object.\n\n    Supported prototypes:\n\n    - dealiasing_setofvar(complex128[][][][], uint8[][][])\n\n    Parameters\n    ----------\n\n    sov : 4d ndarray\n        A set of variables array.\n\n    where_dealiased : 3d ndarray\n        A 3d array of \"booleans\" (actually uint8).\n\n"},
    {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "util3d_pythran",            /* m_name */
    "\nPythran compatible functions: 3d operators (:mod:`fluidsim.operators.util3d_pythran`)\n=====================================================================================\n\n.. autofunction:: dealiasing_setofvar\n\n.. autofunction:: dealiasing_variable\n\n.. autofunction:: urudfft_from_vxvyfft\n\n",         /* m_doc */
    -1,                  /* m_size */
    Methods,             /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
  };
#define PYTHRAN_RETURN return theModule
#define PYTHRAN_MODULE_INIT(s) PyInit_##s
#else
#define PYTHRAN_RETURN return
#define PYTHRAN_MODULE_INIT(s) init##s
#endif
PyMODINIT_FUNC
PYTHRAN_MODULE_INIT(util3d_pythran)(void)
#ifndef _WIN32
__attribute__ ((visibility("default")))
__attribute__ ((externally_visible))
#endif
;
PyMODINIT_FUNC
PYTHRAN_MODULE_INIT(util3d_pythran)(void) {
    #ifdef PYTHONIC_TYPES_NDARRAY_HPP
        import_array()
    #endif
    #if PY_MAJOR_VERSION >= 3
    PyObject* theModule = PyModule_Create(&moduledef);
    #else
    PyObject* theModule = Py_InitModule3("util3d_pythran",
                                         Methods,
                                         "\nPythran compatible functions: 3d operators (:mod:`fluidsim.operators.util3d_pythran`)\n=====================================================================================\n\n.. autofunction:: dealiasing_setofvar\n\n.. autofunction:: dealiasing_variable\n\n.. autofunction:: urudfft_from_vxvyfft\n\n"
    );
    #endif
    if(! theModule)
        PYTHRAN_RETURN;
    PyObject * theDoc = Py_BuildValue("(sss)",
                                      "0.8.5",
                                      "2018-05-04 19:37:52.415400",
                                      "56c2f292466f123700e23eea0d4fceec1cb0517465beed69d5015e99319e6922");
    if(! theDoc)
        PYTHRAN_RETURN;
    PyModule_AddObject(theModule,
                       "__pythran__",
                       theDoc);


    PYTHRAN_RETURN;
}

#endif