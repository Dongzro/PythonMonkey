import pythonmonkey as pm
import sys

def test_eval_dicts():
    d = {"a":1}
    proxy_d = pm.eval("(dict) => { return dict; }")(d)
    assert d is proxy_d

def test_eval_dicts_subdicts():
    d = {"a":1, "b":{"c": 2}}
    
    assert pm.eval("(dict) => { return dict.a; }")(d) == 1.0
    assert pm.eval("(dict) => { return dict.b; }")(d) is d["b"]
    assert pm.eval("(dict) => { return dict.b.c; }")(d) == 2.0

def test_eval_dicts_cycle():
    d: dict = {"a":1, "b":2}
    d["recursive"] = d
    
    assert pm.eval("(dict) => { return dict.a; }")(d) == 1.0
    assert pm.eval("(dict) => { return dict.b; }")(d) == 2.0
    assert pm.eval("(dict) => { return dict.recursive; }")(d) is d["recursive"]

def test_eval_objects():
    pyObj = pm.eval("Object({a:1.0})")
    assert pyObj == {'a':1.0}

def test_eval_objects_subobjects():
    pyObj = pm.eval("Object({a:1.0, b:{c:2.0}})")

    assert pyObj['a'] == 1.0
    assert pyObj['b'] == {'c': 2.0}
    assert pyObj['b']['c'] == 2.0

def test_eval_objects_cycle():
    pyObj = pm.eval("Object({a:1.0, b:2.0, recursive: function() { this.recursive = this; return this; }}.recursive())")
    
    assert pyObj['a'] == 1.0
    assert pyObj['b'] == 2.0
    assert pyObj['recursive'] == pyObj

def test_eval_objects_proxy_get():
    f = pm.eval("(obj) => { return obj.a}")
    assert f({'a':42.0}) == 42.0

def test_eval_objects_proxy_set():
    f = pm.eval("(obj) => { obj.a = 42.0; return;}")
    pyObj = {}
    f(pyObj)
    assert pyObj['a'] == 42.0
    
def test_eval_objects_proxy_keys():
    f = pm.eval("(obj) => { return Object.keys(obj)[0]}")
    assert f({'a':42.0}) == 'a'

def test_eval_objects_proxy_delete():
    f = pm.eval("(obj) => { delete obj.a }")
    pyObj = {'a': 42.0}
    f(pyObj)
    assert 'a' not in pyObj

def test_eval_objects_proxy_has():
    f = pm.eval("(obj) => { return 'a' in obj }")
    pyObj = {'a': 42.0}
    assert(f(pyObj))

def test_eval_objects_proxy_not_extensible():
    assert False == pm.eval("(o) => Object.isExtensible(o)")({})
    assert False == pm.eval("(o) => Object.isExtensible(o)")({ "abc": 1 })
    assert True == pm.eval("(o) => Object.preventExtensions(o) === o")({})

def test_eval_objects_jsproxy_contains():
    a = pm.eval("({'c':5})")
    assert 'c' in a

def test_eval_objects_jsproxy_does_not_contain():
    a = pm.eval("({'c':5})")
    assert not(4 in a)

def test_eval_objects_jsproxy_does_not_contain_value():
    a = pm.eval("({'c':5})")
    assert not(5 in a)

def test_eval_objects_jsproxy_or():
  if sys.version_info[0] >= 3 and sys.version_info[1] >= 9: # | is not implemented for dicts in 3.8 or less
    a = pm.eval("({'c':5})")
    b = pm.eval("({'d':6})")
    c = a | b
    assert a == {'c': 5.0}  
    assert c == {'c': 5.0, 'd': 6.0}   
    assert b == {'d': 6.0} 

def test_eval_objects_jsproxy_or_true_dict_right():
  if sys.version_info[0] >= 3 and sys.version_info[1] >= 9: # | is not implemented for dicts in 3.8 or less
    a = pm.eval("({'c':5})")
    b = {'d': 6.0}
    c = a | b
    assert a == {'c': 5.0}  
    assert c == {'c': 5.0, 'd': 6.0}   
    assert b == {'d': 6.0} 

def test_eval_objects_jsproxy_or_true_dict_left():
  if sys.version_info[0] >= 3 and sys.version_info[1] >= 9: # | is not implemented for dicts in 3.8 or less
    a = {'c':5}
    b = pm.eval("({'d':6})")
    c = a | b
    assert a == {'c': 5.0}  
    assert c == {'c': 5.0, 'd': 6.0}   
    assert b == {'d': 6.0} 

def test_eval_objects_jsproxy_inplace_or():
  if sys.version_info[0] >= 3 and sys.version_info[1] >= 9: # | is not implemented for dicts in 3.8 or less
    a = pm.eval("({'c':5})")
    b = pm.eval("({'d':6})")
    a |= b
    assert a == {'c': 5.0, 'd': 6.0}   
    assert b == {'d': 6.0}       

def test_eval_objects_jsproxy_inplace_or_true_dict_right():
  if sys.version_info[0] >= 3 and sys.version_info[1] >= 9: # | is not implemented for dicts in 3.8 or less
    a = pm.eval("({'c':5})")
    b = {'d':6.0}
    a |= b
    assert a == {'c': 5.0, 'd': 6.0}   
    assert b == {'d': 6.0}       

def test_eval_objects_jsproxy_inplace_or_true_dict_left():
  if sys.version_info[0] >= 3 and sys.version_info[1] >= 9: # | is not implemented for dicts in 3.8 or less
    a = {'c':5.0}
    b = pm.eval("({'d':6})")
    a |= b
    assert a == {'c': 5.0, 'd': 6.0}   
    assert b == {'d': 6.0}   
    assert True == pm.eval("(o) => Object.preventExtensions(o) === o")({ "abc": 1 })

def test_instanceof_object():
    a = {'c':5.0}
    result = [None]
    pm.eval("(result, obj) => {result[0] = obj instanceof Object}")(result, a)
    assert result[0] == True      

def test_eval_objects_proxy_iterate():
    obj = pm.eval("({ a: 123, b: 'test' })")
    result = []
    for i in obj:
        result.append(i)
    assert result == [('a', 123.0), ('b', 'test')]

def test_eval_objects_proxy_repr():
    obj = pm.eval("({ a: 123, b: 'test' , c: { d: 1 }})")
    obj.e = obj # supporting circular references
    expected = "{'a': 123.0, 'b': 'test', 'c': {'d': 1.0}, 'e': [Circular]}"
    assert repr(obj) == expected
    assert str(obj) == expected

def test_eval_objects_proxy_dict_conversion():
    obj = pm.eval("({ a: 123, b: 'test' , c: { d: 1 }})")
    d = dict(obj)
    assert type(obj) is not dict # dict subclass
    assert type(d) is dict # strict dict
    assert repr(d) == "{'a': 123.0, 'b': 'test', 'c': {'d': 1.0}}"
    assert obj.keys() == ['a', 'b', 'c'] # Conversion from a dict-subclass to a strict dict internally calls the .keys() method
    assert list(d.keys()) == obj.keys()
    assert obj == d

def test_eval_objects_jsproxy_get():
    proxy = pm.eval("({a: 1})")
    assert 1.0 == proxy['a']
    assert 1.0 == proxy.a

def test_eval_objects_jsproxy_set():
    proxy = pm.eval("({a: 1})")
    proxy.a = 2.0
    assert 2.0 == proxy['a']
    proxy['a'] = 3.0
    assert 3.0 == proxy.a
    proxy.b = 1.0
    assert 1.0 == proxy['b']
    proxy['b'] = 2.0
    assert 2.0 == proxy.b

def test_eval_objects_jsproxy_length():
    proxy = pm.eval("({a: 1, b:2})")
    assert 2 == len(proxy)

def test_eval_objects_jsproxy_delete():
    proxy = pm.eval("({a: 1})")
    del proxy.a
    assert None == proxy.a
    assert None == proxy['a']

def test_eval_objects_jsproxy_compare():
    proxy = pm.eval("({a: 1, b:2})")
    assert proxy == {'a': 1.0, 'b': 2.0}

def test_eval_objects_jsproxy_contains():
    a = pm.eval("({'c':5})")
    assert 'c' in a

def test_eval_objects_jsproxy_does_not_contain():
    a = pm.eval("({'c':5})")
    assert not(4 in a)

def test_eval_objects_jsproxy_does_not_contain_value():
    a = pm.eval("({'c':5})")
    assert not(5 in a)

def test_eval_objects_jsproxy_or():
  if sys.version_info[0] >= 3 and sys.version_info[1] >= 9: # | is not implemented for dicts in 3.8 or less
    a = pm.eval("({'c':5})")
    b = pm.eval("({'d':6})")
    c = a | b
    assert a == {'c': 5.0}  
    assert c == {'c': 5.0, 'd': 6.0}   
    assert b == {'d': 6.0} 

def test_eval_objects_jsproxy_or_true_dict_right():
  if sys.version_info[0] >= 3 and sys.version_info[1] >= 9: # | is not implemented for dicts in 3.8 or less
    a = pm.eval("({'c':5})")
    b = {'d': 6.0}
    c = a | b
    assert a == {'c': 5.0}  
    assert c == {'c': 5.0, 'd': 6.0}   
    assert b == {'d': 6.0} 

def test_eval_objects_jsproxy_or_true_dict_left():
  if sys.version_info[0] >= 3 and sys.version_info[1] >= 9: # | is not implemented for dicts in 3.8 or less
    a = {'c':5}
    b = pm.eval("({'d':6})")
    c = a | b
    assert a == {'c': 5.0}  
    assert c == {'c': 5.0, 'd': 6.0}   
    assert b == {'d': 6.0} 

def test_eval_objects_jsproxy_inplace_or():
  if sys.version_info[0] >= 3 and sys.version_info[1] >= 9: # | is not implemented for dicts in 3.8 or less
    a = pm.eval("({'c':5})")
    b = pm.eval("({'d':6})")
    a |= b
    assert a == {'c': 5.0, 'd': 6.0}   
    assert b == {'d': 6.0}       

def test_eval_objects_jsproxy_inplace_or_true_dict_right():
  if sys.version_info[0] >= 3 and sys.version_info[1] >= 9: # | is not implemented for dicts in 3.8 or less
    a = pm.eval("({'c':5})")
    b = {'d':6.0}
    a |= b
    assert a == {'c': 5.0, 'd': 6.0}   
    assert b == {'d': 6.0}       

def test_eval_objects_jsproxy_inplace_or_true_dict_left():
  if sys.version_info[0] >= 3 and sys.version_info[1] >= 9: # | is not implemented for dicts in 3.8 or less
    a = {'c':5.0}
    b = pm.eval("({'d':6})")
    a |= b
    assert a == {'c': 5.0, 'd': 6.0}   
    assert b == {'d': 6.0}