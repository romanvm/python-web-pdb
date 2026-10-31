# Copyright (c) 2026 Roman Miroshnychenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Helpers for presenting Python objects as expandable variable trees
"""

import builtins
import inspect
from collections.abc import Mapping, Sequence, Set
from concurrent.futures import Future
from itertools import islice

__all__ = [
    'VariablesRequest',
    'is_dunder',
    'describe',
    'get_namespace_nodes',
    'get_children',
    'resolve_path',
]

MAX_CHILDREN = 300
MAX_REPR_LENGTH = 1000

# Key token kinds
NAME = 'n'  # A name in a namespace dict (globals/locals)
ATTRIBUTE = 'a'
INDEX = 'i'
MAPPING_KEY = 'k'  # Position of a key in mapping iteration order
SET_MEMBER = 's'  # Position of a member in set iteration order

_LEAF_TYPES = (type(None), bool, int, float, complex, str, bytes, bytearray, range)
_ITEMS_ONLY_TYPES = (dict, list, tuple, set, frozenset)
if hasattr(builtins, 'frozendict'):  # Python 3.15+
    _ITEMS_ONLY_TYPES += (builtins.frozendict,)


class VariablesRequest:
    """
    A request for children of a variable tree node

    It is passed from the web-server thread to the debugger thread
    via the shared input queue, and the result is returned via ``future``.
    """

    def __init__(self, scope, path):
        """
        :param scope: ``'globals'`` or ``'locals'``
        :type scope: str
        :param path: a list of ``[kind, value]`` key tokens from the scope root
        :type path: list
        """
        self.scope = scope
        self.path = path
        self.future = Future()


def is_dunder(name):
    return name.startswith('__') and name.endswith('__')


def _safe_repr(obj):
    try:
        value = repr(obj)
    except Exception as exc:  # pylint: disable=broad-except
        value = f'<{type(exc).__name__}: {exc}>'
    if len(value) > MAX_REPR_LENGTH:
        value = value[:MAX_REPR_LENGTH] + '...'
    return value


def _is_expandable(obj):
    if isinstance(obj, _LEAF_TYPES) or inspect.isroutine(obj):
        return False
    if type(obj) in _ITEMS_ONLY_TYPES:
        return len(obj) > 0
    return True


def describe(name, key, obj):
    """
    Describe an object as a variable tree node

    :param name: displayed name
    :type name: str
    :param key: ``[kind, value]`` token to access the object from its parent
    :type key: list
    :param obj: the object to describe
    :return: a JSON-serializable node
    :rtype: dict
    """
    return {
        'name': name,
        'key': key,
        'type': type(obj).__name__,
        'value': _safe_repr(obj),
        'expandable': _is_expandable(obj),
    }


def get_namespace_nodes(namespace):
    """
    Get top-level variable tree nodes for a namespace

    .. note:: special variables that start and end with
        double underscores ``__`` are not included.

    :param namespace: a `dict` of `var_name: var_object` pairs
    :type namespace: dict
    :return: a list of nodes sorted by name
    :rtype: list
    """
    return [
        describe(name, [NAME, name], value)
        for name, value in sorted(namespace.items())
        if not is_dunder(name)
    ]


def _get_attribute_names(obj):
    try:
        names = dir(obj)
    except Exception:  # pylint: disable=broad-except
        return []
    return [name for name in names if not is_dunder(name)]


def _iter_items(obj):
    """Yield ``(name, key, getter)`` tuples for container items"""
    if isinstance(obj, Mapping):
        for i, key in enumerate(obj.keys()):
            yield _safe_repr(key), [MAPPING_KEY, i], lambda k=key: obj[k]
    elif isinstance(obj, Set):
        for i, member in enumerate(obj):
            yield f'[{i}]', [SET_MEMBER, i], lambda m=member: m
    elif isinstance(obj, Sequence) and not isinstance(obj, _LEAF_TYPES):
        for i in range(len(obj)):
            yield f'[{i}]', [INDEX, i], lambda j=i: obj[j]


def _iter_attributes(obj):
    """Yield ``(name, key, getter)`` tuples for non-special attributes"""
    if type(obj) in _ITEMS_ONLY_TYPES:
        return
    for name in _get_attribute_names(obj):
        yield name, [ATTRIBUTE, name], lambda n=name: getattr(obj, n)


def _get_node(name, key, getter):
    try:
        value = getter()
    except Exception as exc:  # pylint: disable=broad-except
        node = describe(name, key, None)
        node['type'] = type(exc).__name__
        node['value'] = f'<{type(exc).__name__}: {exc}>'
        return node
    if key[0] == ATTRIBUTE and inspect.isroutine(value):
        return None
    return describe(name, key, value)


def get_children(obj):
    """
    Get child nodes of an object

    Container items come first, followed by non-special attributes.
    Methods and functions are excluded.

    :param obj: the parent object
    :return: a tuple of a list of child nodes and the count of omitted children
    :rtype: tuple
    """
    children = []
    more = 0
    try:
        for name, key, getter in islice(_iter_items(obj), MAX_CHILDREN):
            children.append(_get_node(name, key, getter))
        if len(children) == MAX_CHILDREN:
            more = len(obj) - MAX_CHILDREN
    except Exception:  # pylint: disable=broad-except
        pass  # Broken container, show what we have got so far
    for name, key, getter in _iter_attributes(obj):
        if len(children) >= MAX_CHILDREN:
            more += 1
            continue
        node = _get_node(name, key, getter)
        if node is not None:
            children.append(node)
    return children, more


def _resolve_key(obj, key):
    kind, value = key
    if kind == ATTRIBUTE and isinstance(value, str):
        try:
            return getattr(obj, value)
        except Exception as exc:
            raise LookupError(f'Unable to get attribute {value!r}') from exc
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise LookupError(f'Invalid key: {key!r}')
    try:
        if kind == INDEX and isinstance(obj, Sequence):
            return obj[value]
        if kind == MAPPING_KEY and isinstance(obj, Mapping):
            return obj[next(islice(obj.keys(), value, None))]
        if kind == SET_MEMBER and isinstance(obj, Set):
            return next(islice(obj, value, None))
    except (StopIteration, IndexError, KeyError) as exc:
        raise LookupError(f'Item not found: {key!r}') from exc
    raise LookupError(f'Invalid key: {key!r}')


def resolve_path(namespace, path):
    """
    Resolve an object by its path from a namespace

    :param namespace: a `dict` of `var_name: var_object` pairs
    :type namespace: dict
    :param path: a list of ``[kind, value]`` key tokens
    :type path: list
    :return: the resolved object
    :raises LookupError: if the path cannot be resolved
    """
    if not path or not isinstance(path, list):
        raise LookupError('Empty path')
    for key in path:
        if not isinstance(key, list) or len(key) != 2:
            raise LookupError(f'Invalid key: {key!r}')
    kind, name = path[0]
    if kind != NAME or not isinstance(name, str) or name not in namespace:
        raise LookupError(f'Name {name!r} is not defined')
    obj = namespace[name]
    for key in path[1:]:
        obj = _resolve_key(obj, key)
    return obj
