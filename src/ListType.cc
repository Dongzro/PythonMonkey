#include "include/ListType.hh"

#include "include/modules/pythonmonkey/pythonmonkey.hh"
#include "include/JSArrayProxy.hh"
#include "include/PyType.hh"
#include "include/pyTypeFactory.hh"

#include <jsfriendapi.h>
#include <jsapi.h>

#include <Python.h>





ListType::ListType() : PyType(PyList_New(0)) {}

ListType::ListType(PyObject *object) : PyType(object) {}

ListType::ListType(JSContext *cx, JS::HandleObject jsArrayObj) {
  JSArrayProxy *proxy = (JSArrayProxy *)PyObject_CallObject((PyObject *)&JSArrayProxyType, NULL);
  proxy->jsObject.set(jsArrayObj);
  this->pyObject = (PyObject *)proxy;
}