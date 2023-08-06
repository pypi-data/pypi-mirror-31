pluckit
======
Easily extract values from collection items.


### Install
```pip install pluckit```


### Usage
```
from pluckit import pluck

data = [
  {'x': 1, 'y': 2},
  {'x': 2, 'y': 4},
  {'x': 3, 'y': 6},
]
pluck(data, 'x')
> [1, 2, 3]


# use Pluckables for built-in functionality

from pluckit.pluckable import PluckableList

PluckableList([
  {'x': 1, 'y': 2},
  {'x': 2, 'y': 4},
  {'x': 3, 'y': 6},
]).pluck('x')
> [1, 2, 3]


# use the Pluckable mixin to build your own

from pluckit import Pluckable
class MyDict(dict, Pluckable): pass

MyDict({
  'home' : {'x' : 1, 'y' : 2},
  'work' : {'x' : 3, 'y' : 6},
}).pluck('x')
> {'home' : 1, 'work' : 3}
```
