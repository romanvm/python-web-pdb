import builtins
import os
import sys
from collections import OrderedDict, namedtuple
from unittest import TestCase, main, skipUnless

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, basedir)

from web_pdb.variables import (  # noqa: E402
    MAX_CHILDREN,
    MAX_REPR_LENGTH,
    get_children,
    get_namespace_nodes,
    resolve_path,
)

Point = namedtuple('Point', 'x y')


class Foo:
    class_attr = 'class'

    def __init__(self):
        self.spam = 'eggs'
        self.items = [1, {'key': (2, 3)}]
        self._protected = {4}

    @property
    def prop(self):
        return 'property'

    @property
    def broken(self):
        raise ValueError('Oops!')

    def method(self):
        pass


def _names(nodes):
    return [node['name'] for node in nodes]


class VariablesTestCase(TestCase):
    """
    Unit tests for variable tree helpers
    """
    def setUp(self):
        self.namespace = {
            '__name__': '__main__',
            'foo': Foo(),
            'number': 42,
            'func': len,
            'empty': [],
            'point': Point(1, 2),
            'odict': OrderedDict(a=1),
            'big': list(range(MAX_CHILDREN + 10)),
        }

    def test_namespace_nodes(self):
        nodes = get_namespace_nodes(self.namespace)
        self.assertEqual(
            ['big', 'empty', 'foo', 'func', 'number', 'odict', 'point'], _names(nodes)
        )
        nodes = {node['name']: node for node in nodes}
        self.assertEqual(
            {'name': 'number', 'key': ['n', 'number'], 'type': 'int', 'value': '42',
             'expandable': False},
            nodes['number'],
        )
        self.assertTrue(nodes['foo']['expandable'])
        self.assertFalse(nodes['func']['expandable'])
        self.assertFalse(nodes['empty']['expandable'])

    def test_object_children(self):
        children, more = get_children(self.namespace['foo'])
        self.assertEqual(0, more)
        self.assertEqual(
            ['_protected', 'broken', 'class_attr', 'items', 'prop', 'spam'], _names(children)
        )
        children = {node['name']: node for node in children}
        self.assertEqual("'property'", children['prop']['value'])
        self.assertEqual('<ValueError: Oops!>', children['broken']['value'])
        self.assertFalse(children['broken']['expandable'])

    def test_container_children(self):
        children, _ = get_children([10, 'a'])
        self.assertEqual(['[0]', '[1]'], _names(children))
        self.assertEqual(['i', 1], children[1]['key'])
        children, _ = get_children({'a': 1, 2: 'b'})
        self.assertEqual(["'a'", '2'], _names(children))
        self.assertEqual(['k', 1], children[1]['key'])
        children, _ = get_children(self.namespace['point'])
        self.assertIn('x', _names(children))
        self.assertIn('[0]', _names(children))

    @skipUnless(hasattr(builtins, 'frozendict'), 'frozendict requires Python 3.15+')
    def test_frozendict(self):
        frozendict = builtins.frozendict
        namespace = {'fd': frozendict(a=1, b=[2]), 'empty': frozendict()}
        nodes = {node['name']: node for node in get_namespace_nodes(namespace)}
        self.assertTrue(nodes['fd']['expandable'])
        self.assertFalse(nodes['empty']['expandable'])
        children, more = get_children(namespace['fd'])
        self.assertEqual(0, more)
        self.assertEqual(["'a'", "'b'"], _names(children))
        self.assertEqual(['k', 1], children[1]['key'])
        self.assertEqual([2], resolve_path(namespace, [['n', 'fd'], ['k', 1]]))

    def test_truncation(self):
        children, more = get_children(self.namespace['big'])
        self.assertEqual(MAX_CHILDREN, len(children))
        self.assertEqual(10, more)
        node = get_namespace_nodes({'s': 'x' * (MAX_REPR_LENGTH * 2)})[0]
        self.assertEqual(MAX_REPR_LENGTH + 3, len(node['value']))

    def test_resolve_path(self):
        obj = resolve_path(self.namespace, [['n', 'foo'], ['a', 'items'], ['i', 1], ['k', 0]])
        self.assertEqual((2, 3), obj)
        obj = resolve_path(self.namespace, [['n', 'foo'], ['a', '_protected'], ['s', 0]])
        self.assertEqual(4, obj)
        for path in (
            [],
            [['n', 'bar']],
            [['a', 'foo']],
            [['n', 'foo'], ['i', 0]],
            [['n', 'foo'], ['a', 'missing']],
            [['n', 'foo'], ['a', 'items'], ['i', 5]],
            [['n', 'foo'], ['a', 'items'], ['i', -1]],
            [['n', 'foo'], 'items'],
        ):
            with self.subTest(path=path):
                with self.assertRaises(LookupError):
                    resolve_path(self.namespace, path)


if __name__ == '__main__':
    main()
