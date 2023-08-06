# Expiring_object 
![[PyPI](https://pypi.python.org/project/expiring_object)](https://img.shields.io/pypi/v/expiring_object.svg)
![License](https://img.shields.io/pypi/l/expiring_object.svg)
![Status](https://img.shields.io/pypi/status/expiring_object.svg)
![Python versions](https://img.shields.io/pypi/pyversions/expiring_object.svg)
![Downloads](https://img.shields.io/pypi/dw/expiring_object.svg)
This module provides a simple way to build self-removal objects

## Examples
```python
import time

from expiring_object import object_factory, Dispatcher

class Stub:
    pass

with Dispatcher(expiring_time=10, maxlen=10) as dp:
    obj = object_factory(Stub(), dp)  # pass object that you want to self-remove and a dispatcher instance
    # do something
    time.sleep(10)
    # the object was self-removed
    print(obj) # raises ReferenceError

```

Also you can use this way:
```python
from weakref import proxy

dp = Dispatcher(10)
dp.start()
some_ref = Stub()
weak_ref = proxy(some_ref)  # a weak reference to an object
dp.add(some_ref)
# you must delete your link to this object
# in another way only handler(if specified) will ba called
del some_ref 
# do something
time.sleep(10)
# the object was self-removed
dp.stop()
del weak_ref  # this proxy object already not needs

```

Also you can pass an object that has a callable attribute named `_handler`
<br>It is calling (and then deleting item too) when the lifetime has expired:
```python
class Stub:
    def _handler(self):
        print('deleting `stub`')
dp.add(Stub())
```
> Note: You should remind that this object must not have another strong references
### License
This project provided by a MIT license

Also all issues are welcome

> Note that it is an alpha branch
