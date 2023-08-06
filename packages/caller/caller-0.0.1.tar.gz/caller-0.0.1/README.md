# caller

Caller is a little library for calling a property as a regular function.

Installation
------------

Install using pip:

    $ pip install caller

Usage
-----

```python
from caller import property

class Foo(object):
    def __init__(self, bar):
        self._bar = bar

    @property
    def bar(self):
        return self._bar

    @bar.setter
    def bar(self, new_bar):
        self._bar = new_bar

foo = Foo('bar')
foo.bar('new bar')

print(foo.bar)
```

Prints

```
new bar
```

Or with a separate caller

```python
class Foo(object):
    ...
    @bar.caller
    def bar(self, new_bar):
        self._bar = new_bar[::-1]
        print(self._bar)

Foo('bar').bar('new bar')
```

Prints

```
rab wen
```

That's all.
