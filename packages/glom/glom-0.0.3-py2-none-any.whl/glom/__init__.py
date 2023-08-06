"""*glom gets results.*

To be more precise, glom helps pull together objects from other
objects in a declarative, dynamic, and downright simple way.

Built with services, APIs, and general serialization in mind, glom
helps filter objects as well as perform deep fetches which would be
tedious to perform in a procedural manner.

Where "schema" and other libraries focus on validation and parsing
less-structured data into Python objects, glom goes the other
direction, producing more-readily serializable data from valid
higher-level objects.

"""

from __future__ import print_function

from collections import OrderedDict

try:
    basestring
except NameError:
    basestring = str


_MISSING = object()


class GlomError(Exception):
    "A base exception for all the errors that might be raised from"
    " calling the glom function."
    pass


class PathAccessError(KeyError, IndexError, TypeError, GlomError):
    '''An amalgamation of KeyError, IndexError, and TypeError,
    representing what can occur when looking up a path in a nested
    object.
    '''
    def __init__(self, exc, seg, path):
        self.exc = exc
        self.seg = seg
        self.path = path

    def __repr__(self):
        cn = self.__class__.__name__
        return '%s(%r, %r, %r)' % (cn, self.exc, self.seg, self.path)

    def __str__(self):
        return ('could not access %r from path %r, got error: %r'
                % (self.seg, self.path, self.exc))


class CoalesceError(GlomError):  # TODO
    pass


class TypeHandler(object):
    def __init__(self, type_obj, get, iterate):
        self.type = type_obj
        if iterate is True:
            iterate = iter
        if iterate is not False and not callable(iterate):
            raise ValueError('expected callable or bool for iterate, not: %r'
                             % iterate)
        self.iterate = iterate
        if not callable(get):
            raise ValueError('expected callable for get, not: %r' % (get,))
        self.get_func = get

    def iter_func(self, target, path=None):
        if not self.iterate:
            msg = 'type %r not registered for iteration' % self.type.__name__
            if path is not None:
                msg += ' (at %r)' % Path(*path)
            raise GlomError(msg)  # TODO: dedicated exception type for this?
        return self.iterate(target)


class Path(object):
    """Used to represent explicit paths when the default 'a.b.c'-style
    syntax won't work or isn't desirable.

    Use this to wrap ints, datetimes, and other valid keys, as well as
    strings with dots that shouldn't be expanded.

    >>> target = {'a': {'b': 'c', 'd.e': 'f', 2: 3}}
    >>> glom(target, {'a_d': Path('a', 'd.e'), 'a_2': Path('a', 2)})
    {'a_de': 'f', 'a_2': 3}
    """
    def __init__(self, *path_parts):
        self.path_parts = path_parts

    def __repr__(self):
        cn = self.__class__.__name__
        return '%s(%s)' % (cn, ', '.join([repr(p) for p in self.path_parts]))


class Literal(object):
    """Used to represent a literal value in a spec. Wherever a Literal
    object is encountered in a spec, it is replaced with its *value*
    in the output.

    This could also be achieved with a callable, e.g., `lambda _:
    'literal'` in the spec, but using a Literal object adds some
    explicitness and clarity.
    """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        cn = self.__class__.__name__
        return '%s(%r)' % (cn, self.value)


# TODO: exception for coalesces that represents all sub_specs tried
class Coalesce(object):
    def __init__(self, *sub_specs, **kwargs):
        self.sub_specs = sub_specs
        self.default = kwargs.pop('default', _MISSING)
        self.skip = kwargs.pop('skip', _MISSING)
        if self.skip is _MISSING:
            self.skip_func = lambda v: False
        elif callable(self.skip):
            self.skip_func = self.skip
        elif isinstance(self.skip, tuple):
            self.skip_func = lambda v: v in self.skip
        else:
            self.skip_func = lambda v: v == self.skip

        self.skip_exc = kwargs.pop('skip_exc', GlomError)
        if kwargs:
            raise TypeError('unexpected keyword args: %r' % (sorted(kwargs.keys()),))


class Glommer(object):
    def __init__(self):
        self._type_map = OrderedDict()
        self._type_tree = OrderedDict()  # see _register_fuzzy_type for details

    def _get_type(self, obj):
        "return the closest-matching type config for an object *instance*, obj"
        try:
            return self._type_map[type(obj)]
        except KeyError:
            closest = self._get_closest_type(obj)
            if closest is not None:
                return self._type_map[closest]
            raise TypeError('expected instance of registered types (%r), not %r'
                            % (', '.join([t.__name__ for t in self._type_map]),
                               obj.__class__.__name__))  # TODO: instance or type repr?

    def _get_closest_type(self, obj, _type_tree=None):
        type_tree = _type_tree if _type_tree is not None else self._type_tree
        default = None
        for cur_type, sub_tree in reversed(type_tree.items()):
            if isinstance(obj, cur_type):
                sub_type = self._get_closest_type(obj, _type_tree=sub_tree)
                ret = cur_type if sub_type is None else sub_type
                return ret
        return default

    def _register_fuzzy_type(self, new_type, _type_tree=None):
        """Build a "type tree", an OrderedDict mapping registered types to
        their subtypes

        The type tree's invariant is that a key in the mapping is a
        valid parent type of all its children.

        Order is preserved such that non-overlapping parts of the
        subtree take precedence by which was most recently added.
        """
        type_tree = _type_tree if _type_tree is not None else self._type_tree

        registered = False
        for cur_type, sub_tree in list(type_tree.items()):
            if issubclass(cur_type, new_type):
                if issubclass(new_type, cur_type):
                    raise ValueError('inheritance cycles not supported'
                                     ' (detected between %r and %r)'
                                     % (new_type, cur_type))
                sub_tree = type_tree.pop(cur_type)  # mutation for recursion brevity
                try:
                    type_tree[new_type][cur_type] = sub_tree
                except KeyError:
                    type_tree[new_type] = OrderedDict({cur_type: sub_tree})
                registered = True
            elif issubclass(new_type, cur_type):
                type_tree[cur_type] = self._register_fuzzy_type(new_type, _type_tree=sub_tree)
                registered = True

        if not registered:
            type_tree[new_type] = OrderedDict()

        return type_tree

    def register(self, target_type, get, iterate=False, exact=False):
        """Register a new type with the Glommer so it will know how to handle
        it as a target.
        """
        self._type_map[target_type] = TypeHandler(target_type, get=get, iterate=iterate)
        if not exact:
            self._register_fuzzy_type(target_type)
        return

    def _get_path(self, target, path):
        try:
            parts = path.split('.')
        except (AttributeError, TypeError):
            parts = getattr(path, 'path_parts', None)
            if parts is None:
                raise TypeError('path expected str or Path object, not: %r' % path)

        cur, val = target, target
        for part in parts:
            try:
                getter = self._get_type(cur).get_func
            except TypeError:
                e = TypeError('type %r not registered for access' % type(cur))
                raise PathAccessError(e, part, parts)
            try:
                val = getter(cur, part)
            except Exception as e:
                raise PathAccessError(e, part, parts)
            cur = val
        return val

    def glom(self, target, spec, **kwargs):
        # TODO: check spec up front
        # TODO: good error
        # TODO: default
        # TODO: de-recursivize this
        # TODO: rearrange the branching below by frequency of use
        path = kwargs.pop('_path', [])

        if isinstance(spec, dict):
            ret = type(spec)()
            # TODO: the above works for dict + ordereddict, but is it
            # sufficient for other cases?

            for field, sub_spec in spec.items():
                ret[field] = self.glom(target, sub_spec)
            return ret
        elif isinstance(spec, list):
            sub_spec = spec[0]
            _iter = self._get_type(target).iter_func

            try:
                iterator = _iter(target, path=path)
            except TypeError as te:
                raise TypeError('failed to iterate on instance of type %r at %r (got %r)'
                                % (target.__class__.__name__, Path(*path), te))

            return [self.glom(t, sub_spec, _path=path + [i]) for i, t in enumerate(iterator)]
        elif isinstance(spec, tuple):
            res = target
            for sub_spec in spec:
                res = self.glom(res, sub_spec, _path=path)
                if not isinstance(sub_spec, list):
                    path = path + [getattr(sub_spec, 'func_name', sub_spec)]  # TODO: py3 __name__ (use inspect)
            return res
        elif callable(spec):
            return spec(target)
        elif isinstance(spec, (basestring, Path)):
            try:
                return self._get_path(target, spec)
            except PathAccessError as pae:
                pae.path = Path(*(path + list(pae.path)))
                raise
        elif isinstance(spec, Coalesce):
            for sub_spec in spec.sub_specs:
                try:
                    ret = self.glom(target, sub_spec)
                    if spec.skip_func(ret):
                        continue
                    return ret
                except spec.skip_exc as e:
                    pass
            if spec.default is not _MISSING:
                return spec.default
            else:
                # TODO: exception for coalesces that represents all sub_specs tried
                raise CoalesceError('no valid values found while coalescing')
        elif isinstance(spec, Literal):
            return spec.value
        else:
            raise TypeError('expected spec to be dict, list, tuple,'
                            ' callable, or string, not: %r' % spec)
        return


_DEFAULT = Glommer()
glom = _DEFAULT.glom
register = _DEFAULT.register


_DEFAULT.register(object, object.__getattribute__)
_DEFAULT.register(dict, dict.__getitem__)
_DEFAULT.register(list, list.__getitem__, True)  # TODO: are iterate and getter mutually exclusive or?


def _main():
    class Example(object):
        pass

    example = Example()
    subexample = Example()
    subexample.name = 'good_name'
    example.mapping = {'key': subexample}

    val = {'a': {'b': 'c'},
           'example': example,
           'd': {'e': ['f'],
                 'g': 'h'},
           'i': [{'j': 'k', 'l': 'm'}],
           'n': 'o'}

    spec = {'a': 'a.b',
            'name': 'example.mapping.key.name',  # test object access
            'e': 'd.e',  # d.e[0] or d.e: (callable to fetch 0)
            'i': ('i', [{'j': 'j'}]),  # TODO: support True for cases when the value should simply be mapped into the field name?
            'n': ('n', lambda n: n.upper()),
            'p': Coalesce('xxx',
                          'yyy',
                          default='zzz')}

    ret = glom(val, spec)

    print('in: ', val)
    print('got:', ret)
    expected = {'a': 'c',
                'name': 'good_name',
                'e': ['f'],
                'i': [{'j': 'k'}],
                'n': 'O',
                'p': 'zzz'}
    print('exp:', expected)

    print(glom(list(range(10)), Path(1)))  # test list getting and Path
    print(glom(val, ('d.e', [(lambda x: {'f': x[0]}, 'f')])))

    class A(object):
        pass

    class B(object):
        pass

    class C(A):
        pass

    class D(B):
        pass

    class E(C, D, A):
        pass

    class F(E):
        pass

    register = _DEFAULT.register
    get = lambda x: x
    for t in [E, D, A, C, B]:
        register(t, get)

    assert _DEFAULT._get_closest_type(F()) is E
    return


if __name__ == '__main__':
    _main()

"""TODO:

* More subspecs
  * dicts
  * lists (indicating iterability)
  * callables (for advanced processing)
* More supported target types
  * Django and SQLAlchemy Models and QuerySets
* Support unregistering types

glom({
    'name': 'name',  # simple get-attr
    'primary_email': 'primary_email.email',  # multi-level get-attr
    'emails': ('email_set', ['email']),  # get-attr + sequence unpack + fetch one attr
    'roles': ('vendor_roles', [{'role': 'role'}]),  # get-attr + sequence unpack + sub-glom
}, contact)

ideas from this:
every value of the dict is moving down a level, the algorithm is to repeatedly
walk down levels via get-attr + sequence unpacks until you run out of levels
and then whatever you have arrived at goes in that spot

you could also maybe glom to a list by just taking the values() of the above dict
glom([
   'name', 'primary_email.email', ('email_set', ['email']), ('vendor_roles', [{'role': 'role'}])
], contact)

would be cool to have glom gracefully degrade to a get_path:

  glob({'a': {'b': 'c'}}, 'a.b') -> 'c'

(spec is just a string instead of a dict, target is still a dict obvs)

---

Need to raise a good exception on failure to fetch. Maybe:

class PathAccessError(KeyError, IndexError, TypeError):
    '''An amalgamation of KeyError, IndexError, and TypeError,
    representing what can occur when looking up a path in a nested
    object.
    '''
    def __init__(self, exc, seg, path):
        self.exc = exc
        self.seg = seg
        self.path = path

    def __repr__(self):
        cn = self.__class__.__name__
        return '%s(%r, %r, %r)' % (cn, self.exc, self.seg, self.path)

    def __str__(self):
        return ('could not access %r from path %r, got error: %r'
                % (self.seg, self.path, self.exc))


Also need the ability to specify defaults if something is not found,
as opposed to raising an error. Default varies by whether or not to
iterate. Empty list if yes, None if no.

"""
